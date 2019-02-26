         function ShowCitiesStats(row) {
             var table = document.getElementById("region_stat");
             var elems = document.querySelectorAll(".active_row");

         [].forEach.call(elems, function (el) {
                 el.classList.remove("active_row");
             });

             var tr = document.getElementById(row.id);
             tr.classList.add('active_row');

             var region_id = row.id;
             // row.classlist.add("active_row");
             // row.style.backgroundColor = "#e6ae7282";
             // row.style.fontWeight = "900";
             var xhr = new XMLHttpRequest();
             var url = "server_address/city_stats/" + region_id;
             xhr.open('GET', url);
             // xhr.responseType = 'text';
             xhr.send();
             xhr.onreadystatechange = function () {
                 if (xhr.readyState === XMLHttpRequest.DONE) {
                     // document.getElementById("city_stat").innerHTML += xhr.responseText;
                     //                     document.getElementById("city_stat").innerHTML = "<caption>Статистика в разрезе городов</caption>" +
                     //                         "<th>Наименование города</th>" + "<th>Количество <br> комментариев</th>" + xhr.responseText;
                     stat_city = JSON.parse(xhr.responseText);
                     var table = document.getElementById('city_stat');

                     for (var i = table.rows.length - 1; i > 0; i--) {
                         table.deleteRow(i);
                     }

                     stat_city.forEach(function (item, i, stat_city) {
                         var row = table.insertRow(table.length);
                         row.id = item[0];
                         var cell1 = row.insertCell(0);
                         var cell2 = row.insertCell(1);
                         cell1.innerHTML = item[1];
                         cell2.innerHTML = item[2];
                     });
                 };
             };
             document.getElementById('city_stats').style.display = "block";
         }

         function HiddenFunction() {
             document.getElementById('city_stats').style.display = "none";
         }
