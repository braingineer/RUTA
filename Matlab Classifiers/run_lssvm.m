%% EXACT PREDICTION
% MAKE MODEL
type = 'function estimation';
X = trainX;
Y = trainY;
kernel = 'RBF_kernel';
gam = 10;
sig2 = 0.2;

% RUN AND TEST
model = initlssvm(X,Y,type,gam,sig2,kernel);
model = trainlssvm(model);
Yp = simlssvm(model, trainX);
disp(' ');
disp('Training data...');
fprintf('MAPE: %f SMAPE: %f\n', mape(Yp, trainY), smape(Yp, trainY));
plotlssvm(model);

Yp = simlssvm(model, testX);
disp(' ');
disp('Testing data...');
fprintf('MAPE: %f SMAPE: %f\n', mape(Yp, testY), smape(Yp, testY));
figure;
plot(1:size(testX,1), testY,'b*');
hold on;
plot(1:size(testX,1), Yp,'r');

%% DIRECTION TESTING
type = 'classification';
X = dir_trainX;
Y = dir_trainY;
kernel = 'RBF_kernel';
gam = 10;
sig2 = 0.2;

% RUN AND TEST
model = initlssvm(X,Y,type,gam,sig2,kernel);
model = trainlssvm(model);
Yp = simlssvm(model, dir_trainX);
disp(' ');
disp('Training data...');
fprintf('Accuracy: %f\n', sum(Yp == dir_trainY)/size(Yp,1));
%plotlssvm(model);

Yp = simlssvm(model, dir_testX);
disp(' ');
disp('Testing data...');
fprintf('Accuracy: %f\n', sum(Yp == dir_testY)/size(Yp,1));
figure;
plot(1:size(testX,1), dir_testY,'b*');
hold on;
plot(1:size(testX,1), Yp,'r.');
ylim([-1 2]);