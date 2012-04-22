function [ mapeval, smapeval ] = regressEval( Xtrain, Ytrain, Xtest, Ytest )
%REGRESSEVAL Fit regression model and evaluate
%   1) Tune best parameters for SVM with RBF kernel
%   2) Train best model
%   3) Evaluate test data

    model = initlssvm(Xtrain, Ytrain, 'function estimation', [], [], 'RBF_kernel');
    
    model = tunelssvm(model, 'simplex', 'crossvalidatelssvm', {10,'mse'});
    %disp(model);
    model = trainlssvm(model);

    Ypred = simlssvm(model, Xtest);
    mapeval = mape(Ypred, Ytest);
    smapeval = smape(Ypred, Ytest);
    
    %fprintf('MAPE: %f SMAPE: %f\n', mapeval, smapeval);
    %figure;
    %plot(1:size(Xtest,1), Ytest,'b*');
    %hold on;
    %plot(1:size(Xtest,1), Ypred,'r');
end

