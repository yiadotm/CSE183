var rates = [
    [10, 0, 0],
    [12, 11000, 22000],
    [22, 44725, 89450],
    [24, 95375, 190750],
    [32, 182100, 364200],
    [35, 231250, 462500],
    [37, 578125, 693750]
];
let inputs;
let spouseCheckbox;

function calculateValues() {
    let income = parseFloat(inputs[0].value) || 0;
    let interest = parseFloat(inputs[1].value) || 0;
    let otherIncome = parseFloat(inputs[2].value) || 0;
    let fedTax = parseFloat(inputs[3].value) || 0;
    let eic = parseFloat(inputs[4].value) || 0;
    let otherTax = parseFloat(inputs[5].value) || 0;

    
    let totalIncome = income + interest + otherIncome;
    document.getElementById("value-4").value = totalIncome.toFixed(2);

    let isJointReturn = spouseCheckbox.checked;
    let standardDeduction = isJointReturn ? 27700 : 13850; 
    document.getElementById('value-5').value = isJointReturn ? 27700 : 13850;

    let taxableIncome = totalIncome - standardDeduction;
    if (standardDeduction > totalIncome) {

        document.getElementById('value-6').value = 0;

    }
    else {
        document.getElementById('value-6').value = taxableIncome.toFixed(2);
    }
    // console.log(totalIncome);
    let line9 = fedTax + eic;
    document.getElementById('value-9').value = line9.toFixed(2);
    
    let tax = calculateTax(taxableIncome, isJointReturn);
    document.getElementById('value-10').value = tax.toFixed(2);

    let totalTax = tax + otherTax;
    document.getElementById('value-12').value = totalTax.toFixed(2);

    let refund = 0;
    let amountOwed = 0;
    if (line9 > totalTax) {
        refund = Math.abs(totalTax - line9);
    }
    else {
        amountOwed = Math.abs(line9 - totalTax);
    }
    document.getElementById('value-13').value = refund.toFixed(2);

    document.getElementById('value-14').value = amountOwed.toFixed(2);
}

function calculateTax(taxableIncome, isJointReturn) {
    let tax = 0;
    for (let i = rates.length - 1; i >= 0; i--) {
        let lowerBound = isJointReturn ? rates[i][2] : rates[i][1];
        if (taxableIncome > lowerBound) {
            let incomeInBracket = taxableIncome - lowerBound;
            tax += incomeInBracket * (rates[i][0] / 100);
            taxableIncome -= incomeInBracket;
        }
    }
    return tax;
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    spouseCheckbox = document.getElementById('spouse');
    if(form) {
        form.addEventListener('input', calculateValues);
    } else {
        console.error('Form not found');
    }

    inputs = Array.from(form.querySelectorAll('.input'));
    

    inputs.forEach(input => {
        input.addEventListener('input', calculateValues);
    });

    spouseCheckbox.addEventListener('change', calculateValues);


});
