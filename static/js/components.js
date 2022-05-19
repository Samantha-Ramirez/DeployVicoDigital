// FUNCTIONS
async function fetchNotifications() {
    const response = await fetch(`/fetch_notification`);
    const notifications = await response.json();
    return notifications['notifications']
};

async function deleteNotifications(sel) {
    const id = sel.value;
    const response = await fetch(`/delete_notification/${id}`);
    document.getElementById('notifications').innerHTML = '<dynamic-notification></dynamic-notification>'
};

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

// NOTIFICATIONS
class notification extends HTMLElement{
    constructor(){
        super();
    }

    async connectedCallback(){
        var me = this;
        let notifications = await fetchNotifications();
        if ((Array.isArray(notifications) === true) && (notifications.length>0) && (Array.isArray(notifications[0]) === true) && notifications[0].length){
            notifications.forEach(function(n){
                me.innerHTML += `
                <div class="card">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-11">
                                ${n[3]}
                                <p class="card-text"><small class="text-muted">${n[2]}</small></p>
                            </div>
                            <div class="col-md-1">
                                <button id="myId" type="submit" name="deleteNotification" class="btn btn-outline-danger btn-circle" value="${n[0]}" onclick="deleteNotifications(this)" style="border-radius: 15px; padding:0; font-size: 0rem;">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle-fill" viewBox="0 0 16 16">
                                        <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/>
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>`
            });
        }else{
            this.innerHTML += `
            <div class="card">
                <div class="card-body" id="notifications">
                    No tienes notificaciones por el momento
                </div>
            </div>`
        }
    }
}

window.customElements.define("dynamic-notification", notification);