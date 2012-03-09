function data = smoothen_of( data, col, win )
%SMOOTHEN_OF smoothens sentiment ratios by moving window averaging
%   data = matrix with one column containing sentiment ratios
%   col  = index of the column containing sentiment ratios
%   win  = size of window for computing moving average

    for i = win:size(data,1)
        sum = 0;
        for j = i-win+1:i
            sum = sum + data(j,col);
        end
        data(i,col) = sum / win;
    end
end

