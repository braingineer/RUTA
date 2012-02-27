% MAKE MODEL
type = 'function approximation';
X = trainX;
Y = trainY;
kernel = 'RBF_kernel';
gam = 10;
sig2 = 0.2;

% RUN AND TEST
model = initlssvm(X,Y,type,gam,sig2,kernel);
model = trainlssvm(model);
Yp = simlssvm(model, trainX);
disp('Training data...');
fprintf('MAPE: %f SMAPE: %f\n', mape(Yp, trainY), smape(Yp, trainY));
plotlssvm(model);

Yp = simlssvm(model, testX);
disp('Testing data...');
fprintf('MAPE: %f SMAPE: %f\n', mape(Yp, testY), smape(Yp, testY));
figure;
plot(1:size(testX,1), testY,'b*');
hold on;
plot(1:size(testX,1), Yp,'r');