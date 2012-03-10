function i0 = get_baseline( djia )
%GET_BASELINE returns baseline matrix
%   djia = matrix with daily closing values
%   the function creates a feature/output matrix with the first column
%   containing the date, the next 3 columns containing the previous 3 days'
%   closing values, and the last column containing the closing value of
%   that day.

    i0 = zeros(size(djia,1)-3, 5);
    
    for i = 4:size(djia,1)
        i0(i-3,:) = [djia(i,1) djia(i-3,2) djia(i-2,2) djia(i-1,2) djia(i,2)];
    end
end

