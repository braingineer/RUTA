function ofmat = smoothen_of( ofmat, col, win )
%SMOOTHEN_OF smoothens sentiment ratios by moving window averaging
%   ofmat = matrix with one column containing sentiment ratios
%   col  = index of the column containing sentiment ratios
%   win  = size of window for computing moving average

    for i = win:size(ofmat,1)
        sum = 0;
        for j = i-win+1:i
            sum = sum + ofmat(j,col);
        end
        ofmat(i,col) = sum / win;
    end
end

