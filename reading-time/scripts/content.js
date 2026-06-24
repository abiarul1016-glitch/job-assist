// function renderReadingTime(article) {
//   // If we weren't provided an article, we don't need to render anything.
//   if (!article) {
//     return;
//   }

//   const text = article.textContent;
//   const wordMatchRegExp = /[^\s]+/g; // Regular expression
//   const words = text.matchAll(wordMatchRegExp);
//   // matchAll returns an iterator, convert to array to get word count
//   const wordCount = [...words].length;
//   const readingTime = Math.round(wordCount / 200);
//   const badge = document.createElement("p");
//   // Use the same styling as the publish information in an article's header
//   badge.classList.add("color-secondary-text", "type--caption");
//   badge.textContent = `⏱️ ${readingTime} min read`;

//   // Support for API reference docs
//   const heading = article.querySelector("h1");
//   // Support for article docs with date
//   const date = article.querySelector("time")?.parentNode;

//   (date ?? heading).insertAdjacentElement("afterend", badge);
// }

// renderReadingTime(document.querySelector("article"));

// const observer = new MutationObserver((mutations) => {
//   for (const mutation of mutations) {
//     // If a new article was added.
//     for (const node of mutation.addedNodes) {
//       if (node instanceof Element && node.tagName === 'ARTICLE') {
//         // Render the reading time for this particular article.
//         renderReadingTime(node);
//       }
//     }
//   }
// });

// // https://developer.chrome.com/ is a SPA (Single Page Application) so can
// // update the address bar and render new content without reloading. Our content
// // script won't be reinjected when this happens, so we need to watch for
// // changes to the content.
// observer.observe(document.querySelector('devsite-content'), {
//   childList: true
// });


// // my personal testing
// function renderAbishan() {

//     const header_badge = document.createElement('h1')
//     header_badge.textContent = 'This is an Abishan Extension effect.'
    
//     const document_header = document.querySelector('h1')
//     document_header.insertAdjacentElement('beforebegin', header_badge)

// }

// renderAbishan()

const find = 'chrome'
const replace = 'Abishan'

// Walk through all text elements on the page
const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);

// capitalize function
function capitalizeFirstLetter(str) {
  if (!str) return ""; // Guard against empty or null strings
  return str.charAt(0).toUpperCase() + str.slice(1);
}

let node;
while (node = walk.nextNode()) {

  // deal with lowercase version of find keyword
  const lower_find = find.toLowerCase()
  node.nodeValue = node.nodeValue.split(lower_find).join(replace);

  // deal with uppercase version of find keyword
  const upper_find = capitalizeFirstLetter(find)
  node.nodeValue = node.nodeValue.split(upper_find).join(replace);

}