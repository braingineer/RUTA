function [ accuracy ] = regressEval( Xtrain, Ytrain, Xtest, Ytest )
%REGRESSEVAL Fit classification model and evaluate
%   1) Tune best parameters for SVM with RBF kernel
%   2) Train best model
%   3) Evaluate test data

    model = initlssvm(Xtrain, Ytrain, 'classification', [], [], 'RBF_kernel');
    
    model = tunelssvm(model, 'simplex', 'crossvalidatelssvm', {10,'misclass'});
    %disp(model);
    model = trainlssvm(model);

    Ypred = simlssvm(model, Xtest);
    accuracy = sum(Ypred == Ytest)/size(Ypred,1);
end

