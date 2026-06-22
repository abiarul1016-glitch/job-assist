// get all input fields
label_fields = document.querySelectorAll('label')

let serverFields = []
let aiFields = []

label_fields.forEach(label => {

    // get placeholder text and send to server
    text = label.textContent.trim()

    if (text.includes('?')) {
        serverFields.push(text)
    } else {
        serverFields.push()
    }

})

// log fields
console.log(serverFields)

async function sendFields(endpoint, payload) {

    const url = `https://incubous-caitlyn-herby.ngrok-free.dev${endpoint}`

    try {
        const response = await fetch(url, 
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            }
        )

        if (!response.ok) {
            console.log(`An error has occured: ${response.status}`)
        }

        const data = await response.json()
        return data
        
    } catch (error) {
        console.log(`Error: ${error}`)
    }

}

const serverFieldsRequest = {
    fields: serverFields
}

const aiFieldsRequest = {
    fields: aiFields
}

async function runApplication() {
    
    data = await sendFields(serverFieldsRequest)
    ai_data = await sendFields(aiFieldsRequest)
    console.log(data)
    console.log(ai_data)

    label_fields.forEach(label => {

        // get input-field
        const input_id = label.getAttribute('for')
        const input_field = document.getElementById(input_id)

        input_field.value = data[label.textContent.trim()]

    })

}

runApplication()