var limit_selector = document.getElementById('limit');
var limit = Number(limit_selector.options[limit_selector.selectedIndex].value);
var offset = limit;
var button_next = document.getElementById('next');
var button_prev = document.getElementById('prev');

function DeleteRowFunction() {
    if (confirm('Подтвердите удаление')) {

        var table = document.getElementById('view_comments').tBodies[0];
        var rowCount = table.rows.length;
        var rows_to_delete = [];
        var exist_rows_to_delete = false;
        for (var i = 1; i < rowCount; i++) {
            var row = table.rows[i];
            var chkbox = row.cells[8].getElementsByTagName('input')[0];
            if (chkbox.checked) {
                var exist_rows_to_delete = true;
                rows_to_delete.push(row.id);
                //                table.deleteRow(i);
                //                rowCount--;
                //                i--;
            }
        }
        if (!exist_rows_to_delete) {
            alert('Не выбраны записи для удаления!');
            return true;
        }

        var xhr = new XMLHttpRequest();
        var url = 'server_address/delete';
        xhr.open('POST', url);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(rows_to_delete));        
        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.responseText == 'OK') {                 
 
                    rows_to_delete.forEach(function (row_id, i, rows_to_delete) {
                        row = document.getElementById(row_id);
                       table.removeChild(row);
                    });
                }
            };
        };


    } else {
        return true;
    }

}


limit_selector.onchange = function () {
    limit = limit_selector.options[limit_selector.selectedIndex].value;
    var xhr = new XMLHttpRequest();
    var url = "set_limit/" + limit;
    offset = Number(limit);
    xhr.open('GET', url);
    xhr.send();


    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            part_comments = JSON.parse(xhr.responseText);
            var table = document.getElementById('view_comments');

            for (var i = table.rows.length - 1; i > 0; i--) {
                table.deleteRow(i);
            }

            part_comments.forEach(function (item, i, part_comments) {
                var row = table.insertRow(table.length);
                row.id = item[0];
                for (var i = 1; i < item.length; i += 1) {
                    row.insertCell(i - 1).innerHTML = item[i];
                }
                row.insertCell(8).innerHTML = '<td><input type="checkbox"></td>';
            });

        };
    };

};


function Pagination() {    
     if (offset>0) {
    var xhr = new XMLHttpRequest();   
    var url = 'server_address/get_comments/' + offset;    
    xhr.open('GET', url);    
    xhr.send();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {

            part_comments = JSON.parse(xhr.responseText);
            if (part_comments.length) {
            var table = document.getElementById('view_comments');

            for (var i = table.rows.length - 1; i > 0; i--) {
                table.deleteRow(i);
            }

            part_comments.forEach(function (item, i, part_comments) {
                var row = table.insertRow(table.length);
                row.id = item[0];
                for (var i = 1; i < item.length; i += 1) {
                    row.insertCell(i - 1).innerHTML = item[i];
                }
                row.insertCell(8).innerHTML = '<td><input type="checkbox"></td>';

            });
            }  else {button_next.disabled = true; }
        
        };
    };
     } else {button_prev.disabled = true;}
    };

function ShiftPrev() {
//    offset = Number(limit_selector.options[limit_selector.selectedIndex].value);
    Pagination(); 
    return offset -= Number(limit);   
}

function ShiftNext() {    
//    offset = Number(limit_selector.options[limit_selector.selectedIndex].value);    
    Pagination();
    offset += Number(limit)    
    return offset;
}
