function scaledData = scale( data )
%SCALE Scale data values between 0 and 1
%   Skips the first col which is date

    days = data(:, 1);
    data = data(:, 2:end);
    
    scaledData = zeros(size(data));

    maxData = max(data);
    minData = min(data);

    for c = 1:size(data,2)
        scaledData(:,c) = (data(:,c) - minData(c)) ./ (maxData(c) - minData(c));
    end

    scaledData = [days scaledData];
end

