document.addEventListener("DOMContentLoaded", function () {
    function fetchOptions(apiUrl, inputId) {
        fetch(apiUrl)
            .then(response => response.json())
            .then(data => enableAutocomplete(inputId, data))
            .catch(error => console.error(`Error loading ${inputId}:`, error));
    }

    function enableAutocomplete(inputId, dataList) {
        const input = document.getElementById(inputId);
        const dataListElement = document.getElementById(inputId + "-list");

        input.addEventListener("input", function () {
            dataListElement.innerHTML = "";
            let suggestions = dataList.filter(item =>
                item.toLowerCase().includes(input.value.toLowerCase())
            );
            suggestions.forEach(suggestion => {
                let option = document.createElement("option");
                option.value = suggestion;
                dataListElement.appendChild(option);
            });
        });
    }

    fetchOptions("/register/api/districts/", "id_district");
    fetchOptions("/register/api/states/", "id_state");
});
