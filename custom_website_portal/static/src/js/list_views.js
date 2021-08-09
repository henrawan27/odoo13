(function() {

    if ($('table').hasClass('o_list_table')){
        var session = {
            'model': document.getElementById('data-list').dataset.model
        }

        function formatCurrency(amount){
            return 'Rp ' + amount;
        }

        function setUpTable(response){
            var records = response['records']
            var fields = response['fields']

            var tHead = '<tr><th><div class="form-check"><input id="check-all" type="checkbox" class="form-check-input position-static"/></div></th>';
            for (var field_name in fields){
                tHead += '<th class="pl-0';
                if (fields[field_name].ttype === 'monetary'){
                    tHead += ' text-right';
                }
                tHead += '">' + fields[field_name].field_description + '</th>';
            }
            tHead += '</tr>';
            document.getElementById('thead_list').innerHTML = tHead;

            var tBody = document.getElementById('tbody_list');
            tBody.innerHTML = '';

            for (var record of records){

                var tr = document.createElement('tr');
                tr.setAttribute('class', 'o_data_row');
                tr.id = 'record-' + record.id;

                var td = document.createElement('td');
                var div = document.createElement('div');
                div.setAttribute('class', 'form-check')

                var input = document.createElement('input');
                input.setAttribute('type', 'checkbox');
                input.setAttribute('class', 'form-check-input position-static');
                input.setAttribute('id', 'check-' + record.id);
                input.onchange = changeCheckboxes;

                div.appendChild(input);
                td.appendChild(div);
                tr.appendChild(td);

                for (var field_name in fields){
                    var field = fields[field_name];

                    var td = document.createElement('td');
                    td.setAttribute('class', 'o_data_cell');

                    var className = ['form-control'];
                    if (record.state === 'draft'){
                        className.push('text-info');
                    }

                    if (field.ttype !== 'selection' && field.ttype !== 'many2one'){
                        var input = document.createElement('input');

                        input.id = 'field_' + field_name + '_' + record.id;
                        input.setAttribute('type', 'text');

                        if (field.ttype == 'monetary'){
                            className.push('text-right');
                        }
                        input.value = record[field_name];

                    } else {
                        var input = document.createElement('select');
                        input.id = 'field_' + field_name + '_' + record.id;

                        var option = document.createElement('option');

                        if (!record[field_name]){
                            option.setAttribute('selected', 'selected');
                        }
                        input.appendChild(option);

                        for (var select in field.selection){
                            var option = document.createElement('option');

                            option.innerHTML = field.selection[select];
                            option.value = select;

                            if ((field.ttype === 'selection' && record[field_name] === select) || (field.ttype === 'many2one' && record[field_name][0] == select)){
                                option.setAttribute('selected', 'selected');
                            }
                            input.appendChild(option);
                        }
                    }

                    input.setAttribute('disabled', 'disabled');

                    input.setAttribute('class', className.join(' '));
                    td.appendChild(input);
                    tr.appendChild(td);
                }
                tBody.appendChild(tr);
            }
        }

        function readRecords(){
            var pageRange = document.getElementById('record_value').value;

            var offset = 0;
            var limit = 20;
            if (pageRange){
                var offsetPage = parseInt(pageRange.split('-')[0]);
                var limitPage = parseInt(pageRange.split('-')[1]);

                if (!isNaN(offsetPage) && !isNaN(limitPage)){
                    offset = Math.max(0, offsetPage - 1);
                    limit = limitPage;
                }
            }

            var csrfToken = document.getElementById('csrf_token').value;

            var formData = new FormData();
            formData.append('csrf_token', csrfToken);
            formData.append('offset', offset);
            formData.append('limit', limit);

            var xmlHttp = new XMLHttpRequest();
            xmlHttp.onreadystatechange = function(){
                if(xmlHttp.readyState == 4 && xmlHttp.status == 200){
                    var response = JSON.parse(xmlHttp.responseText);
                    setUpTable(response);
                    document.getElementById('record_value').value = offset + '-' + Math.min(limit, response.total_records);
                    document.getElementsByClassName('o_pager_limit')[0].innerHTML = response.total_records;
                }
            }
            xmlHttp.open('post', '/portal/read/list/' + session.model);
            xmlHttp.send(formData);
        }

        function openFormView(evt){
            var url = '/portal/form/' + session.model.replace('.', '_');
            var targetId = evt.target.id;

            if (targetId !== 'btn-create'){
                var split = targetId.split('_');
                var recordId = split[split.length - 1];
                url += '/' + recordId;
            }
            window.location.href = url;
        }

        function openModal(text, okFunction){
            createWarning(text);
            document.getElementById('btn-modal-ok').onclick = okFunction;
            $('#modalWarning').modal('show');
        }

        function createWarning(text){
            var modalWarning = document.getElementById('modalWarning');
            var modalBody = modalWarning.getElementsByClassName('modal-body')[0];
            var p = document.createElement('p');
            var warningText = document.createTextNode(text);
            p.appendChild(warningText);
            modalBody.innerHTML = '';
            modalBody.appendChild(p);
        }

        function deleteRecords(evt){
            var activeIds = [];
            var allDraft = true;

            var listCheck = document.querySelectorAll('[id^="check-"]:not(#check-all)');

            for (var checkbox of listCheck){
                if (checkbox.checked){
                    var recordId = checkbox.id.replace('check-', '');
                    var stateElement = document.getElementById('field_state_' + recordId);

                    if (stateElement.value !== 'draft'){
                        allDraft = false;
                        activeIds = [];
                        break;
                    } else {
                        activeIds.push(recordId);
                    }
                }
            }

            if (!allDraft){
                createWarning('You cannot delete records that has been submitted!');
                document.getElementById('btn-modal-ok').removeAttribute('data-dismiss');
            } else {
                document.getElementById('btn-modal-ok').setAttribute('data-dismiss', 'modal');

                var csrfToken = document.getElementById('csrf_token').value;
                var formData = new FormData();
                formData.append('csrf_token', csrfToken);

                var xmlHttp = new XMLHttpRequest();
                xmlHttp.onreadystatechange = function(){
                    if(xmlHttp.readyState == 4 && xmlHttp.status == 200){
                        var response = JSON.parse(xmlHttp.responseText);
                        if (response.code === 0){
                            readRecords();
                            document.getElementById('btn-delete').classList.add('d-none');
                        }
                    }
                }
                var url = '/portal/delete/list/' + session.model + '/' + activeIds.join(',');
                xmlHttp.open('post', url);
                xmlHttp.send(formData);
            }
        }

        function changeCheckboxes(evt){

            var listCheck = document.querySelectorAll('[id^="check-"]:not(#check-all)');

            if (evt.target.id === 'check-all'){
                for (var checkbox of listCheck){
                    checkbox.checked = evt.target.checked;
                }

                if (evt.target.checked){
                    document.getElementById('btn-delete').classList.remove('d-none');
                }
                else {
                    document.getElementById('btn-delete').classList.add('d-none');
                }

            } else {
                var allChecked = true;
                if (evt.target.checked){
                    for (var checkbox of listCheck){
                        if (!checkbox.checked){
                            allChecked = false;
                            break
                        }
                    }
                } else {
                    allChecked = false;
                }
                document.getElementById('check-all').checked = allChecked;

                var anyChecked = false;
                for (var checkbox of listCheck){
                    if (checkbox.checked){
                        anyChecked = true;
                        break;
                    }
                }

                if (anyChecked){
                    document.getElementById('btn-delete').classList.remove('d-none');
                } else {
                    document.getElementById('btn-delete').classList.add('d-none');
                }
            }

        }

        function onChange(evt){
            var targetId = evt.target.id;
            if (targetId){
                if (targetId.startsWith('check-')){
                    changeCheckboxes(evt);
                } else if (targetId === 'record_value'){
                    readRecords();
                }
            }
        }

        function onClick(evt){
            var targetId = evt.target.id;
            if (targetId){
                if (targetId === 'btn-create' || targetId.startsWith('field_')){
                    openFormView(evt);
                } else if (targetId === 'btn-delete'){
                    openModal('The selected records will be deleted. Are you sure want to continue?', deleteRecords);
                }
            }
        }

        function onLoadListView(){
            readRecords();
            window.addEventListener('change', onChange);
            window.addEventListener('click', onClick);
        }

        onLoadListView();
    }

})();