// CONTROLS
class control extends HTMLElement{
    constructor(){
        super();
        this.href;
    }

    static get observedAttributes(){
        return ['href'];
    }

    attributeChangedCallback(nameAttr, oldValue, newValue){
        switch(nameAttr){
            case "href":
                this.href = newValue;
            break;
        }
    }

    connectedCallback(){
        this.innerHTML = `<a class="carousel-control-prev" href="${this.href}" role="button" data-slide="prev">
        <span class="carousel-control-prev-icon" aria-hidden="true" style="position: absolute; top: 80px; left: 10px;"></span>
        <span class="sr-only">Previous</span>
        </a>
        <a class="carousel-control-next" href="${this.href}" role="button" data-slide="next">
        <span class="carousel-control-next-icon" aria-hidden="true" style="position: absolute; top: 80px; right: 10px;"></span>
        <span class="sr-only">Next</span>
        </a>`
    }
}

window.customElements.define("dynamic-control", control);