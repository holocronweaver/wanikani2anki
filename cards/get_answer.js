// Get string containing typed Anki answer.
var get_answer = function()
{
    var htmlTextNodes = [];
    var innerHTMLText = [];
    var htmlNodeLength = document.getElementById('typeans').childNodes.length;
    var firstBr = null;
    var secondBr;

    // Capture each node to array.
    for (i = 0; i < htmlNodeLength; i++)
    {
        htmlTextNodes[i] = document.getElementById('typeans').childNodes[i];
        innerHTMLText[i] = document.getElementById('typeans').childNodes[i].innerHTML;

        // Locate <br> tags for output change markers.
        if (document.getElementById('typeans').childNodes[i].nodeName == "BR")
        {
            /* console.log("Runs if BR");*/
            if (firstBr != null) {
                secondBr = i;
            } else {
                firstBr = i;
            };
        };
    };

    // If answer is correct, firstBr will still be null, so must set to
    // length of typeans.childNode.
    if (firstBr == null) {
        firstBr = htmlNodeLength;
    };

    typedVar = innerHTMLText.slice(0,firstBr).join("");
    return typedVar;
};

// Get string containing typed Anki answer written in Japanese.
var get_japanese_answer = function()
{
    var typedVar = get_answer();

    // Assemble typed and correct answer strings.
    var typeParse = typedVar.replace(/\s|\-|\~|\～/g, '');
    var typedAnswer = typedVar.replace(/\~|\～|-|\s/g,' ');

    if (typedVar.slice(-1) === 'n') {
        typedAnswer = typedVar.substr(0, typedVar.length-1);
        typedAnswer += "ん";
    } else {
        typedAnswer = typedVar.replace(/\~|\～|-/g,' ');
    };

    return [typeParse, typedAnswer];
};

// Get correct answers from front of card.
// Placing invisible answers is a way to get around Anki fields
// otherwise not being directly accessible to JavaScript.
var get_correct_answers = function()
{
    var getcorr = document.getElementById('correctAnswer');
    getcorr = getcorr.innerHTML;
    var correctAnswers = getcorr.split(",");
    for (var i = 0; i < correctAnswers.length; i++) {
        correctAnswers[i] = correctAnswers[i].trim();
    }
    return correctAnswers;
};
