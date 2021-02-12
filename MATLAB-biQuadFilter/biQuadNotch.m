function filterCoefficients = biQuadNotch(frequency,sampleRate,bandWidth)
    
    % create the notch filter coefficients for a biquad filter

    omega = 2 * pi * frequency / sampleRate;
    sn = sin(omega);
    cs = cos(omega);
    alpha = sn * sinh(log(2) / 2 * bandWidth * omega / sn);
    b0 = 1;
    b1 = -2 * cs;
    b2 = 1;
    a0 = 1 + alpha;
    a1 = -2 * cs;
    a2 = 1 - alpha;

    filterCoefficients(1) = b0/a0;
    filterCoefficients(2) = b1/a0;
    filterCoefficients(3) = b2/a0;
    filterCoefficients(4) = a1/a0;
    filterCoefficients(5) = a2/a0;

end