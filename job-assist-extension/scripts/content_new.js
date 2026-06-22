// CLIENT-SIDE LOGIC
// get all input fields from page

    // seperate text-field
        // get labels of input fields
        // associate each label with the actual element itself
        // ask server for simple response of basic data
        
    // text-area field
        // get labels of input fields
        // associate each label with the actual element itself
        // ask server for AI response for questions
        
    // file field
        // get labels of input fields
        // associate each label with the actual element itself
        // ask server for custom resume and cover letter


// send dictionary of labels to server
    // server sends a response of what data should be filled for each input with a specific label
    // application fills in the data





// SERVER-SIDE LOGIC
// receives dictionary of input labels

// text-field
    // MVP: first uses direct comparison to match strings with labels
    // for any keys that are not matched: uses string matching library to match the labels with keys in master profile dictionary

// text-area
    // uses AI, to generate an answer for

// file-field
    // generates tailored resume and cover-letter