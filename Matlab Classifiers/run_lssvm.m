%% PREPROCESS
load DJIA_OF;

% inverting OF sentiment ratio
% OF(:,end) = 1./OF(:,end);
% OF_PP(:,end) = 1./OF_PP(:,end);

djia_of = append_of(DJIA, OF);
djia_ofpp = append_of(DJIA, OF_PP);

% smoothen sentiment ratios with a window size of 3
djia_of = smoothen_of(djia_of, size(djia_of,2)-1, 3);
djia_ofpp = smoothen_of(djia_ofpp, size(djia_ofpp,2)-1, 3);

% scale features to be between [0, 1].  Bollen et al (2010) say that makes
% every input be treated with similar importance.
djia_of = scale(djia_of);
djia_ofpp = scale(djia_ofpp);

% randomize rows?
% djia_of = djia_of(randperm(size(djia_of,1)), :);
% djia_ofpp = djia_ofpp(randperm(size(djia_ofpp,1)), :);

% size of training data
%tsize = ceil(.9 * size(djia_of,1));
tsize = 117;

dir_of = direction_data(djia_of, 4);
dir_ofpp = direction_data(djia_ofpp, 4);

%% VISUALIZING DATA

startDate = datenum('2009-06-16');
endDate   = datenum('2009-12-31');
xData = linspace(startDate, endDate, 139);

plot(xData, djia_of(:,6));
ylim([-.5 2]);
grid on;
set(gca, 'XTick', xData);
hold on;
plot(xData, djia_of(:,5), 'r');
plot(xData, djia_ofpp(:,5), 'g');

yL = get(gca, 'YLim');
line([xData(1) xData(1)], yL, 'Color', 'k');
text(xData(2), 1.25, '06/16/2009');

line([xData(end) xData(end)], yL, 'Color', 'k');
text(xData(end-9), 1.25, '12/31/2009');
%annotation('textarrow', [xData(1), xData(3)], [.9 .9], 'String', '06/16/2009');

datetick('x', 'mmm');
legend('DJIA', 'OF (unproc)', 'OF (preproc)');


%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EXACT PREDICTION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% BASELINE -- ONLY DJIA DATA

disp(' ');
disp('DJIA Data only');
% MAKE MODEL
type = 'function estimation';
X = djia_of(1:tsize-1, 2:end-2);
Y = djia_of(1:tsize-1, end);
testX = djia_of(tsize:end, 2:end-2);
testY = djia_of(tsize:end, end);
kernel = 'RBF_kernel';
gam = 5;
sig2 = .8;

% RUN AND TEST
model = initlssvm(X,Y,type,gam,sig2,kernel);
model = trainlssvm(model);
Yp = simlssvm(model, X);
disp(' ');
disp('Training data...');
fprintf('MAPE: %f SMAPE: %f\n', mape(Yp, Y), smape(Yp, Y));
plotlssvm(model);

Yp = simlssvm(model, testX);
disp(' ');
disp('Testing data...');
fprintf('MAPE: %f SMAPE: %f\n', mape(Yp, testY), smape(Yp, testY));
figure;
plot(1:size(testX,1), testY,'b*');
hold on;
plot(1:size(testX,1), Yp,'r');

%% DJIA DATA WITH UN-PROCESSED OF

disp(' ');
disp('DJIA Data with Unprocessed OF');
% MAKE MODEL
type = 'function estimation';
X = djia_of(1:tsize-1, 2:end-1);
Y = djia_of(1:tsize-1, end);
testX = djia_of(tsize:end, 2:end-1);
testY = djia_of(tsize:end, end);
kernel = 'RBF_kernel';
gam = 5;
sig2 = .8;

% RUN AND TEST
model = initlssvm(X,Y,type,gam,sig2,kernel);
model = trainlssvm(model);
Yp = simlssvm(model, X);
disp(' ');
disp('Training data...');
fprintf('MAPE: %f SMAPE: %f\n', mape(Yp, Y), smape(Yp, Y));
plotlssvm(model);

Yp = simlssvm(model, testX);
disp(' ');
disp('Testing data...');
fprintf('MAPE: %f SMAPE: %f\n', mape(Yp, testY), smape(Yp, testY));
figure;
plot(1:size(testX,1), testY,'b*');
hold on;
plot(1:size(testX,1), Yp,'r');

%% DJIA DATA WITH PRE-PROCESSED OF

disp(' ');
disp('DJIA Data with Pre-Processed OF');
% MAKE MODEL
type = 'function estimation';
X = djia_ofpp(1:tsize-1, 2:end-1);
Y = djia_ofpp(1:tsize-1, end);
testX = djia_ofpp(tsize:end, 2:end-1);
testY = djia_ofpp(tsize:end, end);
kernel = 'RBF_kernel';
gam = 5;
sig2 = .8;

% RUN AND TEST
model = initlssvm(X,Y,type,gam,sig2,kernel);
model = trainlssvm(model);
Yp = simlssvm(model, X);
disp(' ');
disp('Training data...');
fprintf('MAPE: %f SMAPE: %f\n', mape(Yp, Y), smape(Yp, Y));
plotlssvm(model);

Yp = simlssvm(model, testX);
disp(' ');
disp('Testing data...');
fprintf('MAPE: %f SMAPE: %f\n', mape(Yp, testY), smape(Yp, testY));
figure;
plot(1:size(testX,1), testY,'b*');
hold on;
plot(1:size(testX,1), Yp,'r');

%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% DIRECTION TESTING
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% BASELINE -- DJIA DATA ONLY

disp(' ');
disp('Direction testing w/ DJIA Data only');

type = 'classification';
X = dir_of(1:tsize-1, 2:end-2);
Y = dir_of(1:tsize-1, end);
testX = dir_of(tsize:end, 2:end-2);
testY = dir_of(tsize:end, end);
kernel = 'RBF_kernel';
gam = 1;
sig2 = .8;

% RUN AND TEST
model = initlssvm(X,Y,type,gam,sig2,kernel);
model = trainlssvm(model);
Yp = simlssvm(model, X);
disp(' ');
disp('Training data...');
fprintf('Accuracy: %f\n', sum(Yp == Y)/size(Yp,1));
figure;
plot(1:size(X,1), Y,'b*');
hold on;
plot(1:size(X,1), Yp,'r.');
ylim([-1 2]);
%plotlssvm(model);

Yp = simlssvm(model, testX);
disp(' ');
disp('Testing data...');
fprintf('Accuracy: %f\n', sum(Yp == testY)/size(Yp,1));
figure;
plot(1:size(testX,1), testY,'b*');
hold on;
plot(1:size(testX,1), Yp,'r.');
ylim([-1 2]);

%% DJIA DATA W/ UNPROCESSED OF

disp(' ');
disp('Direction testing w/ DJIA & unprocessed OF data');

type = 'classification';
X = dir_of(1:tsize-1, 2:end-1);
Y = dir_of(1:tsize-1, end);
testX = dir_of(tsize:end, 2:end-1);
testY = dir_of(tsize:end, end);
kernel = 'RBF_kernel';
gam = 1;
sig2 = .8;

% RUN AND TEST
model = initlssvm(X,Y,type,gam,sig2,kernel);
model = trainlssvm(model);
Yp = simlssvm(model, X);
disp(' ');
disp('Training data...');
fprintf('Accuracy: %f\n', sum(Yp == Y)/size(Yp,1));
figure;
plot(1:size(X,1), Y,'b*');
hold on;
plot(1:size(X,1), Yp,'r.');
ylim([-1 2]);
%plotlssvm(model);

Yp = simlssvm(model, testX);
disp(' ');
disp('Testing data...');
fprintf('Accuracy: %f\n', sum(Yp == testY)/size(Yp,1));
figure;
plot(1:size(testX,1), testY,'b*');
hold on;
plot(1:size(testX,1), Yp,'r.');
ylim([-1 2]);

%% DJIA DATA W/ PRE-PROCESSED OF

disp(' ');
disp('Direction testing w/ DJIA & pre-processed OF data');

type = 'classification';
X = dir_ofpp(1:tsize-1, 2:end-1);
Y = dir_ofpp(1:tsize-1, end);
testX = dir_ofpp(tsize:end, 2:end-1);
testY = dir_ofpp(tsize:end, end);
kernel = 'RBF_kernel';
gam = 1;
sig2 = .8;

% RUN AND TEST
model = initlssvm(X,Y,type,gam,sig2,kernel);
model = trainlssvm(model);
Yp = simlssvm(model, X);
disp(' ');
disp('Training data...');
fprintf('Accuracy: %f\n', sum(Yp == Y)/size(Yp,1));
figure;
plot(1:size(X,1), Y,'b*');
hold on;
plot(1:size(X,1), Yp,'r.');
ylim([-1 2]);
%plotlssvm(model);

Yp = simlssvm(model, testX);
disp(' ');
disp('Testing data...');
fprintf('Accuracy: %f\n', sum(Yp == testY)/size(Yp,1));
figure;
plot(1:size(testX,1), testY,'b*');
hold on;
plot(1:size(testX,1), Yp,'r.');
ylim([-1 2]);