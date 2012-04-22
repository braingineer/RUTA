function dirdata = direction_data( data )
%DIRECTION_DATA generates binary direction data
%   data = data matrix with last column as the day's value

    dirdata = data;
    
    dirdata(:,end) = (data(:,end) > data(:,end-1));
end

