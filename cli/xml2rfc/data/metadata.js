window.addEventListener('load',addMetadata);

async function addMetadata() {

  // Copy all CSS rules for "#identifiers" to "#metadata"
    try {
        const cssRules = document.styleSheets[0].cssRules;
        for (let i = 0; i < cssRules.length; i++) {
            if (/#identifiers/.exec(cssRules[i].selectorText)) {
                const rule = cssRules[i].cssText.
                             replace('#identifiers','#metadata');
                document.styleSheets[0].
                        insertRule(rule, document.styleSheets[0].cssRules.length);
            }
        }
    } catch (e) {
        console.log(e);
    }

  // Retrieve the "metadata" element from the document
    const div = document.getElementById('metadata');
    if (!div) {
        console.log("Could not locate metadata <div> element");
        return;
    }
    div.style.background='#eee';

  // Insert the metadata block
  // [TODO: make this more sophisticated and linkify the values]
    try {
        const jsonFile = document.URL.replace(/html$/,'json');
        const response = await fetch(jsonFile);
        const metadata = (await response.json())[0];

        const label = {
            'STATUS': 'Status',
            'OBSOLETES': 'Obsoletes',
            'OBSOLETED-BY': 'Obsoleted By',
            'UPDATES': 'Updates',
            'UPDATED-BY': 'Updated By',
            'SEE-ALSO': 'See Also',
            'ERRATA-URL': 'Errata',
        };

        let metadataHTML = "<dl style='overflow:hidden'>";
        ['STATUS', 'OBSOLETES', 'OBSOLETED-BY', 'UPDATES',
         'UPDATED-BY', 'SEE-ALSO', 'ERRATA-URL'].forEach(key => {
            if (metadata[key]) {
                metadataHTML += `<dt>${label[key]}:</dt><dd>${metadata[key]}</dd>`;
            }
        })
                metadataHTML += "</dl>";
        div.innerHTML = metadataHTML;

    } catch (e) {
        console.log(e);
    }
}
