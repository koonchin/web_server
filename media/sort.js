/**
 * 
 * @param {HTMLTableElement} table 
 * @param {number} column 
 * @param {boolean} asc 
 */



function sortTable(table, column, asc = true) {
    const dirModifier = asc ? 1 : -1;
    const tBody = table.tBodies[0];
    const rows = Array.from(tBody.querySelectorAll("tr"));

    // // sort each row
    if (column != 3) {
        sortedRows = rows.sort((a, b) => {
            const aColText = a.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim();
            const bColText = b.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim();

            return aColText > bColText ? (1 * dirModifier) : (-1 * dirModifier);
        });
    } else {
        sortedRows = rows.sort((a, b) => {
            const aColText = parseFloat(a.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim());
            const bColText = parseFloat(b.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim());

            return aColText > bColText ? (1 * dirModifier) : (-1 * dirModifier);
        });
    };
    // const sortedRows = rows.sort((a, b) => {
    //     const aColText = a.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim();
    //     const bColText = b.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim();

    //     return aColText > bColText ? (1 * dirModifier) : (-1 * dirModifier);
    // });


    // remove all existing TRs from the table
    while (tBody.firstChild) {
        tBody.removeChild(tBody.firstChild);
    }

    tBody.append(...sortedRows);


    table.querySelectorAll("th").forEach(th => th.classList.remove("th-sort-asc", "th-sort-desc"));
    table.querySelector(`th:nth-child(${ column + 1})`).classList.toggle("th-sort-asc", asc);
    table.querySelector(`th:nth-child(${ column + 1})`).classList.toggle("th-sort-des", !asc);
}


document.querySelectorAll(".table-sortable th").forEach(headerCell => {
    headerCell.addEventListener("click", () => {
        const tableElement = headerCell.parentElement.parentElement.parentElement;
        const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
        const currentIsAscending = headerCell.classList.contains("th-sort-asc");

        sortTable(tableElement, headerIndex, !currentIsAscending);
    });

});