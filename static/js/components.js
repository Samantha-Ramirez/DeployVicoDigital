// NOTIFICATIONS
class notifications extends HTMLElement{
    constructor(){
        super();
        this.id;
        this.content;
        this.date;
    }

    static get observedAttributes(){
        return ['id', 'content', 'date'];
    }

    attributeChangedCallback(nameAttr, oldValue, newValue){
        switch(nameAttr){
            case "id":
                this.id = newValue;
            break;
            case "content":
                this.content = newValue;
            break;
            case "date":
                this.date = newValue;
            break;
        }
    }

    connectedCallback(){
        this.innerHTML = `
        <div class="row">
            <div class="col-md-11">
                ${this.content}
                <p class="card-text"><small class="text-muted">${this.date}</small></p>
            </div>
            <div class="col-md-1">
                <button id="myId" type="submit" name="deleteNotification" class="btn btn-outline-danger btn-circle" value="${this.id}" onclick="fetchInfo(this)" style="border-radius: 15px; padding:0; font-size: 0rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle-fill" viewBox="0 0 16 16">
                        <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/>
                    </svg>
                </button>
            </div>
        </div>`;
    }
}

window.customElements.define("dynamic-notifications", notifications);

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