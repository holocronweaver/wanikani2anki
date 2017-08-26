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
    typedVar = typedVar.split("-").join("");
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

// Get comma-separated list of answers from front of card.
// Placing invisible answers is a way to get around Anki fields
// otherwise not being directly accessible to JavaScript.
var get_correct_answers = function()
{
    var getcorr = document.getElementById('correctAnswer');
    getcorr = getcorr.innerHTML;
    var answers = getcorr.split(",");
    var correctAnswers = [];
    for (var i = 0; i < answers.length; i++) {
        if (answers[i]) {
            correctAnswers.push(answers[i].trim());
        }
    }
    return correctAnswers;
};

var _check_answer = function(answer)
{
    var typeParse = answer[0];
    var typedAnswer = answer[1];

    var correctAnswers = get_correct_answers();

    // Modify answer output.
    if ((correctAnswers.indexOf(typeParse) > -1) && (!(typeParse == "")))
    {
        var c = "<div id='correct'>"+typedAnswer+"</div>";
        var d = document.getElementById('typeans');
        d.innerHTML = c;
    } else {
        // if (typeParse == "") {
        //     typeParse = "BITTERNESS INTENSIFIES!!!";
        // }
        var e = "<div id='incorrect'>"+typeParse+"</div>";
        var f = document.getElementById('typeans');
        f.innerHTML = e;
    };
};

// Check typed answer. Strict, but allows a list of options.
var check_answer = function()
{
    var answer = get_answer();
    _check_answer([answer, answer]);
};

// Check answer entered in Japanese.
var check_japanese_answer = function()
{
    var answer = get_japanese_answer();
    _check_answer(answer);
};

var check_english_answer = function()
{
    var typed_answer = get_answer();
    var answer = typed_answer.toLowerCase().trim();

    var correctAnswers = get_correct_answers();

    // Modify answer output.
    for (var i = 0; i < correctAnswers.length; i++)
    {
        var correctAnswer = correctAnswers[i].toLowerCase();
        var distance = levenshtein(answer, correctAnswer);
        var length = correctAnswer.length;
        // Correct!
        if ((distance / length < 0.4) && (!(answer == "")))
        {
            var c = "<div id='correct'>"+typed_answer+"</div>";
            var d = document.getElementById('typeans');
            d.innerHTML = c;
            return;
        }
    }

    // Incorrect!
    // if (answer == "") {
    //     answer = "BITTERNESS INTENSIFIES!!!";
    // }
    var e = "<div id='incorrect'>"+typed_answer+"</div>";
    var f = document.getElementById('typeans');
    f.innerHTML = e;
};
