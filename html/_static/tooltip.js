
async function addTooltips(){
    termEls = document.getElementsByClassName("std-term");
    termProms = Array.from(termEls).map(getDescription);
    await Promise.all(termProms);
}

async function getDescription(elem){
    //TODO: could save some requests if we group terms from the same glossarry
    //and extract them from one fetch

    // Fetch the glossary term description, based on the parent anchor element.
    let anchor = elem.parentElement
    let url = new URL(anchor.href);
    let doc = await fetch(url.pathname)
        .then(resp => resp.text())
        .then(txt => new DOMParser().parseFromString(txt,'text/html'))
        .catch(err => {
            console.log("Error", err);
            return
        });

    // build the tooltip and append to the anchor element
    let desc = doc.getElementById(url.hash.substr(1))
                  .nextSibling
                  .textContent;
    let tooltip = document.createElement("div");
    let tooltipTitle = document.createElement("h5")
    let tooltipDesc = document.createElement("p");
    tooltipTitle.textContent= url.hash.substr("#term-".length);
    tooltipDesc.textContent = desc;
    tooltip.classList.add("term-tooltip");
    tooltip.appendChild(tooltipTitle)
    tooltip.appendChild(tooltipDesc)
    anchor.appendChild(tooltip);
}


// TODO: remove debug messages here
setTimeout(() => {
    addTooltips().catch(e => {
        console.log('failed adding toolstips', e)
    }).finally(() => console.log("Done with tooltips"));
}, 1000);
