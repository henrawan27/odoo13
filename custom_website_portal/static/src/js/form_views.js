(function() {'use-strict';

    if ($('main').hasClass('form_layout')) {

        var session = {
            'model': document.getElementById('data').dataset.model,
            'id': document.getElementById('data').dataset.id,
        }

        function updateSession(key, value){
            var previous_value = session[key];
            document.getElementById('data').dataset[key] = value;
            session[key] = value;
        }

        function getForm(){
            var formId = 'form_' + session.model;
            var selector = ['input:not(#csrf_token)', 'select', 'textarea'];

            var extraSelector = [];
            if (session.model === 'hr.expense'){
                extraSelector = ['button#add_documents'];
            }

            for (var i=0; i < extraSelector.length; i++){
                selector.push(extraSelector[i]);
            }

            var forms = document.querySelectorAll(selector.join(','));
            return forms;
        }

        function postForm(){
            var forms = document.querySelector('form');
            var formData = new FormData(forms);

            var request = new XMLHttpRequest();
            request.onreadystatechange = function(){
                if (request.readyState == 4 && request.status == 200){
                    var response = JSON.parse(request.responseText);
                    if (response.code === 0){
                        updateSession('id', response.record.id);
                        updateSession('state', response.record.state);
                    }
                }
            }
            var model = session.model.replace('.', '_')
            if (session.id){
                var url = '/portal/update/form/' + model + '/' + session.id;
            } else {
                var url = '/portal/create/form/' + model;
            }
            request.open('POST', url);
            request.send(formData);
        }

        function validateForm(){
            var forms = getForm();
            var isValid = true;
            for (var form of forms){
                if (form.required && (!form.value || form.value === 'false')){
                    form.classList.add('is-invalid');
                    isValid = false;
                }
            }
            return isValid;
        }

        function changedForm(){

            var forms = getForm();
            var hasChanged = false;
            for (var form of forms){
                if (session.id){
                    if (!('current_form' in session) || ('current_form' in session && session['current_form'][form.id] !== form.value)){
                        hasChanged = true;
                        break;
                    }
                } else {
                    if (!form.value){
                        continue;
                    }
                    var defaultValue = form.dataset.def;
                    if (defaultValue != form.value && form.value !== 'false') {
                        hasChanged = true;
                        break;
                    }
                }
            }
            return hasChanged;
        }

        function createFormSession(){
            var forms = getForm();
            session['current_form'] = {};
            for (var form of forms){
                session['current_form'][form.id] = form.value;
            }
        }

        function toggleDisableForm(){
            var forms = getForm();
            for (var form of forms){
                if (form.dataset.compute){
                    continue;
                }
                if (session.readonly){
                    if (form.dataset.edit !== 'all'){
                        var allowed_edit = form.dataset.edit.split(',');
                    } else {
                        var allowed_edit = [session.state];
                    }
                    if (allowed_edit.indexOf(session.state) != -1){
                        form.removeAttribute('disabled');
                    }
                } else {
                    form.setAttribute('disabled', 'disabled');
                }
            }
        }

        function toggleActionButtons(){
            btnEditStates = document.querySelectorAll('button#btn-save, button#btn-discard');
            btnReadStates = document.querySelectorAll('button#btn-edit, button#btn-create', 'button#btn-submit');

            for (var btnEditState of btnEditStates){
                if (session.readonly){
                    btnEditState.classList.remove('d-none');
                } else {
                    btnEditState.classList.add('d-none');
                }
            }

            for (var btnReadState of btnReadStates){
                if (session.readonly){
                    btnReadState.classList.add('d-none');
                } else {
                    btnReadState.classList.remove('d-none');
                }
            }
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

        function actionBtnEdit(){

            createFormSession();
            toggleDisableForm();
            toggleActionButtons();
            updateSession('readonly', false);
        }

        function actionBtnCreate(){
            window.location.href = '/portal/form/' + session.model.replace('.', '_');
        }

        function actionBtnSave(){

            if (session.id){
                if (changedForm()){
                    if (!validateForm()){
                        return;
                    }
                    postForm();
                }
            } else {
                if (!validateForm()){
                    return;
                }
                postForm();
            }

            toggleDisableForm();
            toggleActionButtons();
            updateSession('readonly', true);
            delete session.current_form;
        }

        function actionBtnDiscard(){
            if (session.model === 'hr.expense'){
                var url = '/portal/list/' + session.model.replace('.', '_');
            } else if (session.model == 'hr.employee'){
                var url = '/portal/home/';
            }
            if (!changedForm()){
                window.location.href = url;
            } else {
                createWarning('The record has been modified, your changes will be discarded. Do you want to proceed?');
                document.getElementById('btn-modal-ok').onclick = function(){window.location.href = url};
                $('#modalWarning').modal('show');
            }
        }

        function changeFiles() {
            var files = document.getElementById('documents');
            var attachmentIds = document.getElementById('attachment_ids').value.split(',');

            var newIds = [];
            for (var attachmentId of attachmentIds){
                newIds.push(attachmentId);
            }

            var children = '';
            for (var file of files.files){

                var name = file.name;
                var duplicate = false;

                for(var j=0; j < newIds.length; j++){
                    if (name === newIds[j]){
                        duplicate = true;
                        break;
                    }
                }

                if (duplicate){
                    alert("Can't add attachments with same filename!");
                    document.getElementById('documents').value = null;
                    return;
                }

                var tr = document.createElement('tr');
                tr.setAttribute('id', 'row-' + name)

                var td1 = document.createElement('td');
                var td2 = document.createElement('td');
                var td3 = document.createElement('td');
                td3.setAttribute('class', 'text-right');

                var filename = document.createTextNode(name);
                var size = document.createTextNode(file.size);

                var a = document.createElement('a');
                a.setAttribute('type', 'button');
                a.setAttribute('href', '#');

                var span = document.createElement('span');
                span.setAttribute('class', 'fa fa-trash');
                span.setAttribute('id', 'delete-' + name);
                a.appendChild(span);

                td1.appendChild(filename);
                td2.appendChild(size);
                td3.appendChild(a);

                tr.appendChild(td1);
                tr.appendChild(td2);
                tr.appendChild(td3);

                document.getElementById('modal-attachment').appendChild(tr);
                newIds.push(name);
            }

            var attachmentNumber = parseInt(document.getElementById('attachment_number').innerHTML) + files.files.length;
            document.getElementById('attachment_number').innerHTML = attachmentNumber;
            document.getElementById('attachment_ids').value = newIds.join(',');
        }

        function createActionButtons(actionButton){
            var button = document.createElement('button');
            var text = document.createTextNode(actionButton[2]);
            button.appendChild(text);
            button.setAttribute('id', actionButton[0]);
            button.setAttribute('class', 'btn ' + actionButton[1]);
            button.onclick = actionButton[3];
            return button;
        }

        function setUpActionButtons(){
            var actionButtons = [
                ['btn-edit', 'btn-primary', 'Edit', actionBtnEdit],
                ['btn-create', 'btn-secondary ml-2', 'Create', actionBtnCreate],
                ['btn-save', 'btn-primary', 'Save', actionBtnSave],
                ['btn-discard', 'btn-secondary ml-2', 'Discard', actionBtnDiscard]
            ]

            var extraButtons = [];
            if (session.model === 'hr.employee'){
                actionButtons.splice(1, 1);
            }

            for (var i=0; i < extraButtons.length; i++){
                actionButtons.push(extraButtons[i]);
            }

            var parentActionButtons = document.getElementsByClassName('o_actions_' + session.model)[0];

            for (var actionButton of actionButtons){
                var button = createActionButtons(actionButton);
                if (session.readonly){
                    if (actionButton[0] === 'btn-save' || actionButton[0] === 'btn-discard') {
                        button.classList.add('d-none');
                    }
                } else {
                    if (actionButton[0] === 'btn-edit' || actionButton[0] === 'btn-create') {
                        button.classList.add('d-none');
                    }
                }
                parentActionButtons.appendChild(button);
            }
        }

        function changeSelect(evt, el){
            if (el) {
                var select = el;
            } else {
                var select = evt.target;
            }
            if (!select.value || select.value === 'false'){
                select.selectedIndex = 1;
                select.value = 'false';
                select.style.color = 'rgba(102, 102, 102, .4)';
            } else {
                select.style.color = 'inherit';
            }
        }

        function createForm(response){
            var fields = response.fields;
            var record = response.records[0];

            while (document.getElementsByTagName('field').length){
                var fieldElement = document.getElementsByTagName('field')[0];

                var name = fieldElement.getAttribute('name');
                var placeholder = fieldElement.getAttribute('placeholder');
                var required = fieldElement.getAttribute('required');
                var compute = fieldElement.getAttribute('compute');
                var accept = fieldElement.getAttribute('accept');
                var edit = fieldElement.getAttribute('edit');

                if (!edit){
                    edit = 'all';
                }

                var field = fields[name];
                var classes = fieldElement.getAttribute('class');
                if (!classes){
                    classes = 'form-control'
                }

                var input = '';

                if (!placeholder && field.ttype !== 'binary'){
                    input += '<label for="' + name + '" class="control-label o_font_custom">' + field.field_description + '</label>';
                }

                if (field.ttype === 'binary'){
                    input += '<div id="' + name + '_container" class="o_field_image oe_avatar">';
                    var src = '/web/static/src/img/placeholder.png';
                    if (record){
                        if (record[name]){
                            src = 'data:image/*; base64,' + record[name];
                        }
                    }
                    input += '<img id="' + name + '_img" name="' + name + '_img" src="' + src + '" class="img img-fluid"></img>';
                    input += '<div id="control_avatar" class="o_form_image_controls">';
                    input += '<button type="button" id="edit_avatar" class="fa fa-pencil fa-lg float-left o_select_file_button" title="Edit" aria-label="Edit"></button>';
                    input += '<button type="button" id="delete_avatar" class="fa fa-trash-o fa-lg float-right o_clear_file_button" title="Clear" aria-label="Clear"></button>';
                    input += '<div class="o_hidden_input_file d-none" aria-atomic="true">';
                    input += '<input type="file" id="' + name + '" name="' + name + '" class="' + classes + '" accept="' + accept + '" data-edit="all"/>';
                    input += '<input id="' + name + '_src" name="' + name + '_src" class="' + classes + '" data-edit="all"/>';
                    input += '</div></div></div>';

                } else if (field.ttype !== 'many2one' && field.ttype !== 'selection'){

                    if (field.ttype === 'monetary' || (field.ttype === 'float' && name.includes('amount'))){
                        input += '<div class="input-group"><div class="input-group-prepend"><span class="input-group-text">Rp</span></div>';
                    }

                    if (field.ttype === 'text'){
                        input += '<textarea row="3"';
                    } else if (field.ttype === 'date'){
                        input += '<input type="date"';
                    } else if (field.ttype === 'monetary' || field.ttype === 'float' || field.ttype === 'integer'){
                        input += '<input type="number"';
                    } else {
                        input += '<input type="text"';
                    }

                    input += ' name="' + name + '" id="' + name + '" class="' + classes + '"';

                    if (placeholder){
                        input += ' placeholder="' + placeholder + '"';
                    }

                    if (required){
                        input += ' required="required"';
                    }

                    if (compute){
                        input += ' data-compute="compute"';
                    }

                    if (record){
                        if (record[name]){
                            input += ' value="' + record[name] + '"';
                        }
                    } else if (field.def){
                        input += ' value="' + field.def + '"';
                    }

                    if (record || compute){
                        input += ' disabled="disabled"';
                    }

                    input += ' data-edit="' + edit + '" data-def="' + field.def + '"/>';

                    if (field.ttype === 'monetary' || (field.ttype === 'float' && name.includes('amount'))){
                        input += '</div>';
                    }

                } else {
                    input += '<select name="' + name + '" id="' + name + '" class="' + classes + '"';

                    if (required){
                        input += ' required="required"';
                    }

                    if (compute){
                        input += ' data-compute="compute" disabled="disabled"';
                    }

                    if (record || compute){
                        input += ' disabled="disabled"';
                    }

                    if (placeholder){
                        if (record){
                            if (!record[name]){
                                input += ' style="color: rgba(102, 102, 102, .4);"';
                            }
                        }
                    }

                    input += ' data-edit="' + edit + '" data-def="' + field.def + '">';

                    if (!required){
                        input += '<option value=""/>';
                    }

                    if (!placeholder){
                        placeholder = '';
                    }

                    if (!record){
                        input += '<option value="false" selected="selected" hidden="hidden">' + placeholder + '</option>';
                    } else {
                        if (!record[name]){
                            input += '<option value="false" selected="selected" hidden="hidden">' + placeholder + '</option>';
                        }
                    }

                    for (var select in field.selection){
                        input += '<option value="' + select + '"';
                        if (record){
                            if ((select == record[name][0] && field.ttype === 'many2one') || (select == record[name] && field.ttype === 'selection')){
                                input += ' selected="selected"';
                            }
                        }
                        input += '>' + field.selection[select] + '</option>';
                    }

                    input += '</select>';
                }
                fieldElement.parentElement.innerHTML = input;
            }

            if (session.model === 'hr.expense'){
                while (document.getElementsByTagName('attachment').length){
                    var fieldElement = document.getElementsByTagName('attachment')[0];

                    var name = fieldElement.getAttribute('name');
                    var type = fieldElement.getAttribute('type');

                    var input = '';
                    if (type === 'button'){
                        var attachmentNumber = 0;
                        if (record){
                            attachmentNumber = record.attachment_number;
                        }
                        input += '<button id="' + name + '" name="' + name + '" type="button" class="btn btn-primary" data-toggle="modal" data-target="#attachmentModal"><span id="attachment_number">' + attachmentNumber + '</span> Documents</button>';
                    } else if (type === 'list'){
                        var listName = [];
                        if (record){
                            for (var attachment of record.attachments){
                                listName.push(attachment.name);
                            }
                        }
                        input += '<input id="' + name + '" name="' + name + '" data-edit="all" type="hidden" value="' + listName.join(',') + '"/>';
                    } else if (type === 'file'){
                        input += '<input id="' + name + '" name="' + name + '" data-edit="all" type="file" multiple="true" class="hidden-attachments file"/>';
                    }
                    fieldElement.parentElement.innerHTML = input;
                }

                if (record){
                    var attachmentNames = '';
                    for (var attachment of record.attachments){
                        attachmentNames += '<tr id="row-' + attachment.name + '"><td>' + attachment.name + '</td><td>' + attachment.file_size + '</td><td class="text-right"><a type="button" href="#"><span class="fa fa-trash" id="delete-' + attachment.name + '"/></a></td></tr>';
                    }
                    document.getElementById('modal-attachment').innerHTML = attachmentNames;
                }
            }
        }

        function setUpInitForm(){
            var csrfToken = document.getElementById('csrf_token').value;

            var formData = new FormData();
            formData.append('csrf_token', csrfToken);

            var xmlHttp = new XMLHttpRequest();
            xmlHttp.onreadystatechange = function(){
                if (xmlHttp.readyState == 4 && xmlHttp.status == 200){
                    var response = JSON.parse(xmlHttp.responseText);
                    createForm(response);

                    var state = 'draft';
                    var readonly = false;
                    if (response.records.length){
                        state = response.records[0].state;
                        readonly = true;
                    }
                    if (session.model !== 'hr.employee'){
                        updateSession('state', state);
                    }
                    updateSession('readonly', readonly);
                    setUpActionButtons();
                }
            }
            if (session.id){
                var url = '/portal/read/form/' + session.model + '/' + session.id;
            } else {
                var url = '/portal/read/form/' + session.model + '/new';
            }
            xmlHttp.open('post', url);
            xmlHttp.send(formData);
        }

        function changeTotalAmount(){
            var unitAmount = document.getElementById('unit_amount').value;
            var quantity = document.getElementById('quantity').value;
            document.getElementById('total_amount').value = unitAmount * quantity;
        }

        function deleteAttachment(targetId){
            if (!session.readonly){
                var fileName = targetId.replace('delete-', '');
                document.getElementById('row-' + fileName).remove();
                var attachmentIds = document.getElementById('attachment_ids');

                if (attachmentIds){
                    attachmentIds = attachmentIds.value.split(',');
                    var newAttachmentIds = [];
                    for (var attachment of attachmentIds){
                        if (attachment !== fileName){
                            newAttachmentIds.push(attachment);
                        }
                    }
                    document.getElementById('attachment_ids').value = newAttachmentIds.join(',');
                    document.getElementById('attachment_number').innerHTML = newAttachmentIds.length;
                }
            }
        }

        function changeAvatar(evt){
            var target = evt.target;
            if (target.files && target.files[0]){
                var reader = new FileReader();

                reader.onload = function (e) {
                    document.getElementById('image_1920_img').setAttribute('src', e.target.result);
                    var fileName = document.getElementById('image_1920').value.replace('C:\\fakepath\\', '');
                    document.getElementById('image_1920_src').value = fileName;
                };

                reader.readAsDataURL(target.files[0]);
            }
        }


        function onChange(evt){
            var targetId = evt.target.id;
            if (targetId){
                if (session.model === 'hr.expense'){
                    if (targetId === 'documents'){
                        changeFiles();
                    } else if (targetId === 'product_id'){
                        document.getElementById('unit_amount').value = 1000;
                        changeTotalAmount();
                    } else if (targetId === 'unit_amount' || targetId === 'quantity'){
                        changeTotalAmount();
                    }
                } else if (session.model === 'hr.employee'){
                    if (targetId === 'image_1920'){
                        changeAvatar(evt);
                    }
                }
                if (evt.target.tagName === 'SELECT'){
                    changeSelect(evt);
                }
            }
        }

        function onClick(evt){
            var targetId = evt.target.id;
            if (targetId){
                if (session.model === 'hr.expense'){
                    if (targetId === 'add_documents'){
                        document.getElementById('documents').click();
                    }
                } else if (session.model === 'hr.employee'){
                    if (targetId === 'edit_avatar'){
                        if (!session.readonly){
                            document.getElementById('image_1920').click();
                        }
                    }
                    else if (targetId === 'delete_avatar'){
                        if (!session.readonly){
                            document.getElementById('image_1920_img').setAttribute('src', '/web/static/src/img/placeholder.png');
                            document.getElementById('image_1920_src').value = 'default';
                        }
                    }
                }

                if (targetId.startsWith('delete-')){
                    deleteAttachment(targetId);
                }
            }
        }

        function onLoadFormView(){
            setUpInitForm();
            window.addEventListener('click', onClick);
            window.addEventListener('change', onChange);
        }

        onLoadFormView();
    }
})();