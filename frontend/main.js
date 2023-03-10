$(document).ready(function () {
    // Create search input element on top of table for each column
    $('#table thead th.colSearch').each(function () {
        $(this).html('<input type="text" placeholder="Search column" />');
    });
    // Create table
    var table = $('#table').DataTable({
        dom: 'Blprtlip',
        scrollX: true,
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
        ajax: {
            url: 'data.json',
            dataSrc: function(json) {
                // Update asof dom element with asof attribute from data.json. Then
                // pass data attribute along for datatables to display.
                document.querySelector("#asof").textContent = json.asof
                return json.data
            }
        },
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
    // Remove "dt-buttons" from container because it messes up layouting
    document.querySelector(".dt-buttons.btn-group.flex-wrap").classList.remove("dt-buttons");
    // Small manipulations to have top pagination and nr display dropdown next to each other
    document.querySelector("#table_length").classList.add("float-start");
    document.querySelector("#table_paginate").classList.add("float-end");
});
