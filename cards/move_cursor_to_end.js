// Fix WanaKana moving cursor haphazardly to and fro.
var moveCursorToEnd = function(input) {
    var target = input.target;
    var endIndex = target.value.length;
    if (target.setSelectionRange) {
        return target.setSelectionRange(endIndex, endIndex);
    }
}

var input = document.getElementById('typeans');
input.addEventListener('keydown', moveCursorToEnd);
