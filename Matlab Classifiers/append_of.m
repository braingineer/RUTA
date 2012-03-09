function newdata = append_of( data, of_mat)
%APPEND_OF appends OF sentiment ratio to existing data matrix
%   data = data matrix with day in col 1, value in last col, and features
%           in between.
%   of_mat = matrix with day in col 1, pos val in col 2, neg val in col 3,
%           and ratio in col 4
%   tricky because data matrix has weekends missing.  first columns in the
%   two matrices need to be matched before appending sentiment ratio to
%   data.

    d_counter = 1;
    o_counter = 1;
    
    newdata = zeros(size(data,1), size(data,2)+1);
    while true
        % check if same day
        if data(d_counter,1) == of_mat(o_counter,1)
            % same days, append sentiment ratio before last col
            newdata(d_counter,:) = ...
                [data(d_counter,1:end-1) of_mat(o_counter,end) data(d_counter,end)];
            % meh, as long as it gets the job done
            
            % move counters forward
            d_counter = d_counter + 1;
            o_counter = o_counter + 1;
        else
            % move o_counter forward -- note, this because of an assumed
            % structure of the matrices. respect my authoritah!
            o_counter = o_counter + 1;
        end
        
        % check if end
        if d_counter > size(data,1)
            break;
        end
    end
end

