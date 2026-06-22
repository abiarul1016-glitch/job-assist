const MAIN_URL = 'https://incubous-caitlyn-herby.ngrok-free.dev'
let PAGE_TEXT_CONTENT = ''
let jobContextReady = null

// MAIN CODE
runApplication()

async function runApplication() {

    // establish new context
    PAGE_TEXT_CONTENT = ''
    jobContextReady = null
    const newAIContext = await newAI()

    if (!newAIContext) {
        console.error('Failed to initialize a clean AI context session. Aborting.');
        document.body.removeAttribute('data-autofill-processed')
        return;
    }
    console.log(newAIContext)

    MASTER_PROFILE = await getMasterProfile()
    
    if (!MASTER_PROFILE) {
        console.log('The application cannot reach the Master Profile which is required. Please ensure the FastAPI server is running to continue.')
        document.body.removeAttribute('data-autofill-processed')
        return
    }

    // testing purposes
    console.log(MASTER_PROFILE)

    // give the AI context of the page
    // NOTE: need safety mechanism for askAI later, as we are unsure that updateAI is complete by the time it gets there.
    await scrapeJobDetails()
    jobContextReady = updateAIJobContext()
    
    // get as many input fields as possible
    const inputFields = document.querySelectorAll('input, textarea, select, [contenteditable="true"], [role="textbox"]')
    
    // given an input field: pipeline
    for (const inputField of inputFields) {

        await inputFieldPipeline(inputField)

    }

    console.log("Autofill Pipeline execution complete!")

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


    // extract text content
    let text_content = await extractFieldContext(inputField)
    
    if (text_content) {

        inputFieldDetails['text_content'] = text_content

    } else {

        // guard clause, as no need to continue if no identifying text can be found
        return

    }
    

    // first pass, of simple matching - and filling in response
    if (inputFieldDetails.text_content.length <= 20) {
        
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
            
        }
        
        else {

            // let user handle empty, simple field
            return

        }

        // commenting out later, to avoid uneeded LLM usage, can implement back in later.
        // else {

        //     inputFieldDetails['answer'] = await askAI(inputFieldDetails.text_content)
        //     console.log('AI Match: ', inputFieldDetails['answer'])

        // }

    } else if (inputFieldDetails.text_content.includes('?')) {
        
        // third pass - genAI response
        inputFieldDetails['answer'] = await askAI(inputFieldDetails.text_content)
        console.log('AI Match: ', inputFieldDetails['answer'])

    }

    // fill in details as every filter returns something
    await simpleFill(inputFieldDetails)

    return inputFieldDetails

}


async function extractFieldContext(inputField) {
    
    let contextText = "";

    // 1. Check for standard placeholders or standard text elements
    if (inputField.placeholder) {
        contextText = inputField.placeholder;
    }

    // 2. Check for explicit HTML Labels using the "for" attribute
    if (!contextText && inputField.id) {
        const explicitLabel = document.querySelector(`label[for="${CSS.escape(inputField.id)}"]`);
        if (explicitLabel) {
            contextText = explicitLabel.innerText;
        }
    }

    // 3. Check for implicit/nested HTML labels (where the input is inside a label tag)
    if (!contextText) {
        const parentLabel = inputField.closest('label');
        if (parentLabel) {
            // Use a regex trick to filter out text belonging to nested elements if needed
            contextText = parentLabel.innerText;
        }
    }

    // 4. Check Accessibility (ARIA) Labels - heavily used by modern React/Vue forms
    if (!contextText) {
        contextText = inputField.getAttribute('aria-label') || 
                      inputField.getAttribute('aria-placeholder');
    }

    // 5. Fallback to the raw HTML name or ID attribute (e.g. name="first_name" gives great context)
    if (!contextText) {
        contextText = inputField.getAttribute('name') || inputField.id || "";
    }

    // Clean up extra whitespace, newlines, and trailing colons common in labels (e.g. "First Name:" -> "First Name")
    return contextText.replace(/\s+/g, ' ').replace(/:$/, '').replace(/[*:]/g, '').trim();

}


async function simpleFill(inputFieldDetails) {
    
    const element = inputFieldDetails.inputField;
    const val = inputFieldDetails.answer;

    if (!element || !val) return;

    element.focus();

    // METHOD 1: The standard approach for traditional fields
    if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA' || element.tagName === 'SELECT') {
        element.value = val;
    } 
    // METHOD 2: Fallback for custom rich-text/div fields (e.g. contenteditable)
    else {
        element.innerText = val;
    }

    // METHOD 3: The Framework Backdoor (Crucial for React 16+)
    // Frameworks often intercept standard setters. We can force a native value update:
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
        window.HTMLInputElement.prototype, 
        'value'
    )?.set;
    
    const nativeTextAreaValueSetter = Object.getOwnPropertyDescriptor(
        window.HTMLTextAreaElement.prototype, 
        'value'
    )?.set;

    if (element.tagName === 'INPUT' && nativeInputValueSetter) {
        nativeInputValueSetter.call(element, val);
    } else if (element.tagName === 'TEXTAREA' && nativeTextAreaValueSetter) {
        nativeTextAreaValueSetter.call(element, val);
    }

    // METHOD 4: Fire comprehensive updates so the page processes the change
    const events = ['input', 'change', 'blur'];
    events.forEach(eventType => {
        element.dispatchEvent(new Event(eventType, { bubbles: true, cancelable: true }));
    });

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
