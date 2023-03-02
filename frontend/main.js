console.log('main.js')

$(document).ready(function () {
    $('#table').DataTable({
        ajax: 'data.json',
        columns: [
            { data: 'title' },
            { data: 'summary' },
        ],
    });
});