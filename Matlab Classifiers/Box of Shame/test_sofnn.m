function prediction = test_sofnn( net, data_x, data_y )
%TEST_SOFNN Simulator for a SOFNN

    % SUBFUNCTION RUN_NET
    % takes sofnn and an example set of inputs as an input and runs a
    % simulation of the net to generate an output value.
    % also returns the maximum activation value at the EBF layer and the
    % index of the corresponding neuron -- needed to learn the structure
    function y = run_net( net, d_x )
        % LAYER 1: INPUT LAYER
        % for each input vector column, it is converted into a matrix such 
        % that there are n repetitions of the input vector across columns.
        % This aids matrix arithmetic and serves no other purpose.
        input = repmat(d_x', 1, net.NumEBFNeurons);
        
        % LAYER 2: EBF LAYER
        % What follows is a complicated-looking, but rather simple arithmetic
        % computation that produces the o/p for each EBF neuron (as a
        % column)
%         disp(d_x')
%         disp(net.MemFunCenters)
%         disp(net.MemFunWidths)
        opEBFNeurons = exp(-1* sum(((input-net.MemFunCenters).^2)...
                                        ./ (2*(net.MemFunWidths.^2))))'; 
        
        % LAYER 3: NORMALIZED LAYER
        % need to normalize the output of the neurons -- divide each by the
        % sum of all outputs
        opNormNeurons = opEBFNeurons ./ (sum(opEBFNeurons));
        
        % LAYER 4: WEIGHTED LAYER
        wts = reshape(net.Params', size(d_x,2)+1, net.NumEBFNeurons)';
        weightedBias = (wts * [1 d_x]')';
        
        % LAYER 5: OUTPUT LAYER
        y = weightedBias * opNormNeurons;
    end

    % ------------------------- MAIN ----------------------------- %
    
    data_x = data_x + .0001;
    data_y = data_y + .0001;
    prediction = zeros(size(data_y));
    
    for i=1:size(data_x,1)
        prediction(i) = run_net(net, data_x(i,:));
    end
end