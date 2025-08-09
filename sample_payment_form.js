// Sample React component with intentional issues
var React = require('react');
var PropTypes = require('prop-types');

function PaymentForm(props) {
    var [amount, setAmount] = React.useState('');
    var [cardNumber, setCardNumber] = React.useState('');
    
    var handleSubmit = function(e) {
        e.preventDefault();
        if (amount == '') {
            alert('Amount is required');
            return;
        }
        
        // TODO: Validate card number
        props.onSubmit({amount: amount, cardNumber: cardNumber});
    };
    
    return React.createElement('form', {onSubmit: handleSubmit},
        React.createElement('input', {
            type: 'text',
            placeholder: 'Amount',
            value: amount,
            onChange: function(e) { setAmount(e.target.value) }
        }),
        React.createElement('input', {
            type: 'text', 
            placeholder: 'Card Number',
            value: cardNumber,
            onChange: function(e) { setCardNumber(e.target.value) }
        }),
        React.createElement('button', {type: 'submit'}, 'Submit Payment')
    );
}

module.exports = PaymentForm;
