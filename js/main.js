function findProperty() {

    const request = document.getElementById("propertyRequest").value;
    const result = document.getElementById("aiResult");

    if (request.trim() === "") {
        result.innerText = "Please describe the property you are looking for.";
        return;
    }

    result.innerText = "Finding properties that match your requirements...";

}

function filterProperties() {

    const searchText =
        document.getElementById("searchInput").value.toLowerCase();

    const type =
        document.getElementById("propertyType").value;

    const price =
        document.getElementById("priceFilter").value;

    const properties =
        document.querySelectorAll(".property-card");


    properties.forEach(function(property) {

        const location =
            property.dataset.location;

        const propertyType =
            property.dataset.type;

        const propertyPrice =
            Number(property.dataset.price);


        const locationMatch =
            location.includes(searchText);

        const typeMatch =
            type === "all" ||
            propertyType === type;

        const priceMatch =
            price === "all" ||
            propertyPrice <= Number(price);


        if (locationMatch && typeMatch && priceMatch) {

            property.style.display = "block";

        } else {

            property.style.display = "none";

        }

    });

}

function sendInquiry() {

    const message =
        document.getElementById("detailsMessage");

    message.innerText =
        "Please login to send an inquiry to the property owner.";

}


function saveProperty() {

    const message =
        document.getElementById("detailsMessage");

    message.innerText =
        "Property saved successfully!";

}
