// const AWS = require('aws-sdk');
var sqs;

class EasySQS {
    constructor(config) {
        AWS.config.update(config);
        AWS.config.update({region: 'us-east-1'});
        sqs = new AWS.SQS();
    }

    send(message, queueUrl) {
    	var params = {
    		MessageBody: message,
    		QueueUrl: queueUrl,
    		DelaySeconds: 0
    	};

    	
    	return new Promise((resolve, reject) => {
	    	sqs.sendMessage(params, (err, data) => {
	    		if (err) {
	    			reject(err);
	    		} else {
	    			resolve(data);
	    		}
	    	});
	    });
    }

    receive(queueUrl) {
    	var params = {
    		QueueUrl: queueUrl,
    		VisibilityTimeout: 100 // 10 second wait time
    	};

    	
    	return new Promise((resolve, reject) => {
	    	sqs.receiveMessage(params, (err, data) => {
	    		if (err) {
	    			reject(err);
	    		} else {
	    			resolve(data);
	    		}
	    	});
	    });
    }

    delete(receiptHandle, queueUrl) {
    	var params = {
    		QueueUrl: queueUrl,
    		ReceiptHandle: receiptHandle
    	};
    	
    	return new Promise((resolve, reject) => {
	    	sqs.deleteMessage(params, (err, data) => {
	    		if (err) {
	    			reject(err);
	    		} else {
	    			resolve(data);
	    		}
	    	});
	    });
    }
}

export {EasySQS};