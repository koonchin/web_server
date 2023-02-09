const indexImage = [0, 1, 2, 3, 4, 5, 6, 7, 8];
let arrIndexDelete = [];

function readURL(input) {
    let number = input.id.split("-");
    console.log(number);
    let indexInputImage = "";
    let sizeImage = 100;
    let idNumber = 0;
    if (number[1] !== null && number[1] !== undefined) {
        indexInputImage = "-" + number[1];
        idNumber = number[1];
    }
    let strIdInputImage = '#input-image' + indexInputImage;
    console.log(strIdInputImage);
    let strIdInputWarp = '#file-input-wrap-id' + indexInputImage;
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        CheckAndClearIconRemoveMiniByNumberFormat(indexInputImage);
        reader.onload = function(e) {
            $(strIdInputImage).html(`<img id="logo" name="logo" src="${e.target.result}" alt="your image" width="${sizeImage}" height="${sizeImage}" />`);
            $(strIdInputWarp).append('<span class="file-input__remove-mini" id=remove-id' + indexInputImage + ' onclick="ClearImage(' + idNumber + ')" ><i class="bx bx-x"></i></span>');
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function ClearImage(id) {
    let numberFormat = "";
    if (id !== undefined && id >= 1) { numberFormat = "-" + id; }
    CheckAndClearIconRemoveMiniByNumberFormat(numberFormat);
    arrIndexDelete.push(id);
    let strIdInputImage = '#input-image' + numberFormat;
    $(strIdInputImage).html(`<i class="bx bx-plus-circle file-input__icon"></i><span class="file-input__text"></span>`);
}

function ClearImageAll() {
    $.each(indexImage, function(i) {
        let strFormatIndex = "";
        if (i >= 1)
            strFormatIndex = "-" + i;
        let strIdRemove = 'remove-id' + strFormatIndex;
        let checkImage = document.getElementById(strIdRemove);
        if (checkImage !== null) { ClearImage(i); }
    });
}

function CheckPictureAndSize() {
    let result = [false, false, -1];
    $.each(indexImage, function(i) {
        let strFormatIndex = "";
        if (i >= 1)
            strFormatIndex = "-" + i;
        let strIdImage = "#fInsertFile" + strFormatIndex;
        let objFile = $(strIdImage);
        if (objFile.val() !== '') {
            result[0] = true;
            var ext = objFile.val().split('.').pop().toLowerCase();
            var fsize = objFile[0].files[0].size;
            if (fsize > 1048576) {
                result[0] = false;
                result[1] = true;
                result[2] = i;
                return false;
            }
        }
    });
    return result;
}

function SetBuildFileName() {
    let result = [];
    $.each(indexImage, function(i) {
        let fileKeyValue = {};
        let strFormatIndex = "";
        if (i >= 1)
            strFormatIndex = "-" + i;
        let strIdImage = "#fInsertFile" + strFormatIndex;
        let objFile = $(strIdImage);
        fileKeyValue.fileName = 'file-' + i;
        fileKeyValue.fileValue = objFile[0].files[0];
        if (fileKeyValue.fileValue !== null && fileKeyValue.fileValue !== undefined) { result.push({ fileKeyValue: fileKeyValue }); }
    });
    return result;
}

function GetIndexImageDelete() { return Array.from(new Set(arrIndexDelete)); }

function ClearIndexImageDelete() { arrIndexDelete = []; }

function ClearFileUploadMultipleImageAll() {
    $.each(indexImage, function(i) {
        let strIdImage = "#fInsertFile";
        let strFormatIndex = "";
        if (i >= 1)
            strFormatIndex = "-" + i;
        strIdImage = strIdImage + strFormatIndex;
        $(strIdImage).val(null);
    });
}

function ClearIconRemoveMiniAll() { $('.file-input__remove-mini').remove(); }

function CheckAndClearIconRemoveMiniByNumberFormat(numberFormat) { let item = document.getElementById("remove-id" + numberFormat); if (item) { item.parentNode.removeChild(item); } }