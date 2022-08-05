// get the selector element first
const selector = document.getElementById("options");
console.log(selector.value); //debug
// initialization
// since the default value of the selctor is the first option, we set the rest to "hide"
document.getElementById("br1").style.display = 'initial';
document.getElementById("br2").style.display = 'None';
document.getElementById("br3").style.display = 'None';
document.getElementById("mc_input_label").style.display = 'None';
// for mc options we iterate though an array of options
var mcs = document.getElementsByName("mc");
document.getElementById("mclabel1").style.display = 'None';
document.getElementById("mclabel2").style.display = 'None';
document.getElementById("mclabel3").style.display = 'None';
for (x of mcs) {
    console.log(x); //debug
    x.style.display = 'None';
}
document.getElementById("text_input").style.display = 'None';
document.getElementById("text_input_label").style.display = 'None';

// onchange event attribute calls the following function
selector.onchange = function () {
    console.log(selector.value) //debug
    if (selector.value != 1) {
        // if current option selected is not the first one then hide all it's components
        document.getElementById("br1").style.display = 'None';
        document.getElementById("number_input").style.display = 'None';
        document.getElementById("number_input_label").style.display = 'None';
    }
    else {
        // else show them 
        document.getElementById("br1").style.display = 'initial';
        document.getElementById("number_input").style.display = 'initial';
        document.getElementById("number_input_label").style.display = 'initial';
    }
    if (selector.value != 2) {
        // if current option selected is not the second one then hide all it's components
        document.getElementById("br2").style.display = 'None';
        document.getElementById("text_input").style.display = 'None';
        document.getElementById("text_input_label").style.display = 'None';

    }
    else {
        // else show them
        document.getElementById("br2").style.display = 'initial';
        document.getElementById("text_input").style.display = 'initial';
        document.getElementById("text_input_label").style.display = 'initial';
    }

    if (selector.value != 3) {
        // if current option selected is not the third one then hide all it's components
        document.getElementById("br3").style.display = 'None';
        document.getElementById("mc_input_label").style.display = 'None';
        var mcs = document.getElementsByName("mc");
        document.getElementById("mclabel1").style.display = 'None';
        document.getElementById("mclabel2").style.display = 'None';
        document.getElementById("mclabel3").style.display = 'None';
        for (x of mcs) {
            console.log(x); //debug
            x.style.display = 'None';
        }
    }
    else {
        // else show them
        document.getElementById("br3").style.display = 'initial';
        document.getElementById("mc_input_label").style.display = 'initial';
        var mcs = document.getElementsByName("mc");
        document.getElementById("mclabel1").style.display = 'initial';
        document.getElementById("mclabel2").style.display = 'initial';
        document.getElementById("mclabel3").style.display = 'initial';
        for (x of mcs) {
            console.log(x); //debug
            x.style.display = 'initial';
        }
    }
};
