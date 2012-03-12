function normdata = normalize( data )
%SCALE Normalize each column of data matrix
%   Skips the first col which is date

    days = data(:, 1);
    data = data(:, 2:end);
    
    normdata = zeros(size(data));

    meanData = mean(data);
    stdData = std(data);

    for c = 1:size(data,2)
        normdata(:,c) = (data(:,c) - meanData(c)) ./ stdData(c);
    end

    normdata = [days normdata];
end

