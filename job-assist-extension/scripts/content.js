const MAIN_URL = 'https://incubous-caitlyn-herby.ngrok-free.dev'
let PAGE_TEXT_CONTENT = ''
let jobContextReady = null

// MAIN CODE
runApplication()

async function runApplication() {

    MASTER_PROFILE = await getMasterProfile()
    
    if (!MASTER_PROFILE) {
        console.log('The application cannot reach the Master Profile which is required. Please ensure the FastAPI server is running to continue.')
        return
    }

    // testing purposes
    console.log(MASTER_PROFILE)

    // give the AI context of the page
    // NOTE: need safety mechanism for askAI later, as we are unsure that updateAI is complete by the time it gets there.
    scrapeJobDetails()
    jobContextReady = updateAIJobContext()
    
    // get input fields - abstract
    const inputFields = document.querySelectorAll('input, textarea, select')
    
    // given an input field: pipeline
    for (const inputField of inputFields) {

        await inputFieldPipeline(inputField)

    }

}

// a function which requests the server for a new session with the LLM, this ensures each application is context-aware, and is not mangled by others
async function newAI() {

    const endpoint = '/newAI'
    const url = `${MAIN_URL}${endpoint}`

    return fetch(url, {
        method: 'GET',
        headers: {
            // This header tells ngrok to bypass the warning screen
            'ngrok-skip-browser-warning': 'true',
            'Accept': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
        return response.json()
    })
    .then(data => data)
    .catch(error => {
        console.error('Error:', error)
        return false
    })

}

async function scrapeJobDetails() {

    let current_page_text = ''

    // 1. Look for structured search engine data on the page
    const jsonLdScript = document.querySelector('script[type="application/ld+json"]');
    
    if (jsonLdScript) {
        try {
            const data = JSON.parse(jsonLdScript.innerText);
            // If it's a JobPosting schema, this is pure gold for an AI
            if (data['@type'] === 'JobPosting' || data['@context']?.includes('schema.org')) {
                console.log("Found clean structured job data!");
                current_page_text = JSON.stringify(data);

                PAGE_TEXT_CONTENT += current_page_text
                return current_page_text;
            }
        } catch (e) {
            // Fallback to text scraping if JSON parsing fails
        }
    }
    
    // 2. Fallback if no structured metadata is found
    const elements = document.querySelectorAll('h1, h2, h3, p, li');
    
    // 3. extreme fallback
    if (!elements) {

        current_page_text = document.body.innerText.trim()
        PAGE_TEXT_CONTENT += current_page_text

        // if any page-specific return is required
        return current_page_text

    }
    
    let dynamicText = "";

    elements.forEach(el => {

        const text = el.innerText.trim();
        // Ignore tiny fragments or massive navigation text blocks
        if (text.length > 10 && text.length < 1000) {
            dynamicText += text + "\n";
        }

    });

    current_page_text = dynamicText.trim();

    PAGE_TEXT_CONTENT += current_page_text
    return current_page_text;

}


async function updateAIJobContext(jobDetails=PAGE_TEXT_CONTENT) {

    endpoint = '/updateAI'
    url = `${MAIN_URL}${endpoint}`

    const payload = {
        query: jobDetails,
    };

    try {
        const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify(payload)
        });

        if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        return data

    } catch (error) {

        console.error('Error during POST request:', error);
        return false

    }

}


async function getMasterProfile() {
    const endpoint = '/master-profile/'
    const url = `${MAIN_URL}${endpoint}`

    return fetch(url, {
        method: 'GET',
        headers: {
            // This header tells ngrok to bypass the warning screen
            'ngrok-skip-browser-warning': 'true',
            'Accept': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
        return response.json()
    })
    .then(data => data)
    .catch(error => {
        console.error('Error:', error)
        return false
    })

}


async function inputFieldPipeline(inputField) {

    // initialize a Javascript Object so that this input field can be easily refrenced later
    const inputFieldDetails = {
        'inputField': inputField,
        'id': inputField.id,
        'type': inputField.tagName
    }


    // identify where the text content would be depending on the input type. NOTE: MUST STILL CONSIDER LABELS
    if (inputFieldDetails['type'] === 'INPUT') {

        text_content = inputField.placeholder
        
    } else if (inputFieldDetails['type'] === 'TEXTAREA') {
        
        text_content = inputField.textContent
        
    }
    
    if (text_content) {

        inputFieldDetails['text_content'] = text_content

    } else {

        // guard clause, as no need to continue if no identifying text can be found
        return

    }
    

    // first pass, of simple matching - and filling in response
    if (inputFieldDetails.text_content.length <= 25) {
        
        let match = await directMatch(inputFieldDetails.text_content)
        
        if (match) {
            
            console.log('Direct Match: ', match)

            // given the key returned by the directMatch function, index into to, to associate the answer for the input with it
            inputFieldDetails['answer'] = MASTER_PROFILE[match]
            
        } else if (match = await fuzzyMatch(inputFieldDetails.text_content)) {
            
            // second pass, of fuzzy matching
            console.log('Fuzzy Match: ', match)

            // given the key returned by the fuzzyMatch function (server-side), index into to, to associate the answer for the input with it
            inputFieldDetails['answer'] = MASTER_PROFILE[match]
            
        } else {

            inputFieldDetails['answer'] = await askAI(inputFieldDetails.text_content)
            console.log('AI Match: ', inputFieldDetails['answer'])

        }

    } else {
        
        // third pass - genAI response
        inputFieldDetails['answer'] = await askAI(inputFieldDetails.text_content)
        console.log('AI Match: ', inputFieldDetails['answer'])

    }

    // fill in details as every filter returns something
    await simpleFill(inputFieldDetails)

    return inputFieldDetails

}


async function simpleFill(inputFieldDetails) {
    
    inputFieldDetails.inputField.value = inputFieldDetails.answer

    // needed to force frameworks to register change
    inputFieldDetails.inputField.dispatchEvent(new Event('input', { bubbles: true }));
    inputFieldDetails.inputField.dispatchEvent(new Event('change', { bubbles: true }));


}


async function directMatch(inputFieldText) {

    /*

    Input: input field text
    Returns: the relevant key in the master profile dictionary

    This function matches a given input field's text with the relevant key in the master profile, for quick input filling
    
    Will be updated to use the switch statement.
    TODO: in an update, we will instead iterate through the keys of the profile (cleaning them first: lowercase + swap underscore with space), and then compare, so that this function still works, as more keys are added.

    */

    clean_text = inputFieldText.toLowerCase()

    if (clean_text.includes('first name')) {

        return 'first_name'
        
    } else if (clean_text.includes('middle name')) {
        
        return 'middle_name'
        
    } else if (clean_text.includes('last name')) {
        
        return 'last_name'
    
    } else if (clean_text.includes('email')) {
        
        return 'email'
    
    } else if (clean_text.includes('github')) {
        
        return 'github_url'
    
    } else if (clean_text.includes('linkedin')) {
        
        return 'linkedin_url'

    } else {

        return false

    }

}


async function fuzzyMatch(inputFieldText) {

    const endpoint = '/fuzzy-match/'
    const url = `${MAIN_URL}${endpoint}${inputFieldText}`

    return fetch(url, {
        method: 'GET',
        headers: {
            // This header tells ngrok to bypass the warning screen
            'ngrok-skip-browser-warning': 'true',
            'Accept': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
        return response.json()
    })
    .then(data => data)
    .catch(error => console.error('Error:', error))

}


async function askAI(inputFieldText) {

    endpoint = '/askAI'
    url = `${MAIN_URL}${endpoint}`

    const payload = {
        query: inputFieldText,
    };

    // add verification that Job Context has loaded, using jobContextReady
    if (jobContextReady) {
        console.log('Awaiting backend job context confirmation before generating answer...');
        const isContextLoaded = await jobContextReady;
        if (!isContextLoaded) {
            console.warn('Proceeding with AI generation, but backend context update failed.');
        }
    }

    try {
        const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify(payload)
        });

        if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        return data

    } catch (error) {

        console.error('Error during POST request:', error);

    }

    // return fetch(url, {
    // method: 'POST',
    // headers: {
    //     'Content-Type': 'application/json'
    // },
    // body: JSON.stringify(payload)
    // })
    // .then(response => {
    //     if (!response.ok) {
    //     throw new Error(`HTTP error! Status: ${response.status}`);
    //     }
    //     return response.json();
    // })
    // .then(data => data)
    // .catch(error => console.error('Error:', error));

}
