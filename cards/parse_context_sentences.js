// Split context sentences into separate lines.
var context = document.getElementById('context-sentences');
if (context)
{
    var sentences = context.innerHTML.split('::context::');
    var html = '';
    for (var i = 0; i < sentences.length; i++)
    {
        sentences[i] = sentences[i].split('::translation::');
        html += sentences[i][0] + '<br>';
        html += sentences[i][1];
        if (i < sentences.length - 1) html += '<br>';
    }
    context.innerHTML = html;
}
