console.log('main.js')

$(document).ready(function () {
    // Create search input element on top of table for each column
    $('#table thead th.colSearch').each(function () {
        $(this).html('<input type="text" placeholder="Search" />');
    });
    // Create table
    var table = $('#table').DataTable({
        dom: 'Brtlip',
        buttons: {
            buttons: [
                {
                    extend: 'excelHtml5',
                    text: "Download as Excel",
                    autoFilter: true,
                    className: 'btn-primary btn-sm',
                }
            ],
            dom: {
                button: {
                    className: 'btn'
               },
            }
        },
        ajax: 'data.json',
        columns: [
            { data: 'date' },
            {
                data: {
                    "_": "title",
                    "display": "title__display"
                }
            },
            { data: 'category' },
            { data: 'author' },
            {
                data: {
                    "_": "summary",
                    "display": "summary__display"
                }
            },
        ],
        // Bind search event to column search elements
        initComplete: function () {
            // Apply the search per column
            this.api()
                .columns()
                .every(function (i) {
                    var that = this;
                    $('input', `th.colSearch:eq(${i})`).on('keyup change clear', function () {
                        if (that.search() !== this.value) {
                            that.search(this.value).draw();
                        }
                    });
                });
            },
        });
    // Link excel download to dedicated button
    table.buttons().container().appendTo( $('#mainHeader') );

    // Load and display asof timestamp
    fetch('asof.json')
        .then(response => response.json())
        .then(json => document.querySelector("#asof").textContent = json["asof"])
});
