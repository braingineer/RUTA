function i0 = get_baseline( djia, n )
%GET_BASELINE returns baseline matrix
%   djia = matrix with daily closing values
%   n    = number of previous days to use as features
%   the function creates a feature/output matrix with the first column
%   containing the date, the next n columns containing the previous n days'
%   closing values, and the last column containing the closing value of
%   that day.

    i0 = zeros(size(djia,1)-n, n+2);
    
    for i = n+1:size(djia,1)
        temp = djia(i,1);
        for j=n:-1:1
            temp = [temp djia(i-j,2)];
        end
        temp = [temp djia(i,2)];
        i0(i-n,:) = temp;
    end
end

