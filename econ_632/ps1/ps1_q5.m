% Clear everything
clear

% Set random number generator's seed
rng(632)

% Set number of people n, number of and products per market J, and number
% of markets M
n = 10000;
J = 3;
M = 100;

% Get m = m(i) for each individual
m = ceil((1:n)' * (M/n));

% Set up xi, where the [m,j] element of this vector equals xi_{mj} = xi_j
%mu_xi = [10,20,15];  % Means of the quality distribution for each alternative
%sigma2_xi = 10;  % Variance of the quality distribution
mu_xi = [1,2,0];
xi = ones(M,1) * mu_xi;

% Draw xi as N(mu_xi,sigma_xi)
%xi = randn(M,J) * sqrt(sigma2_xi) + ones(M,1)*mu_xi;

% Set up Z, where the mth element of this column vector equals Z_m
mu_Z = 0;  % Mean of base distribution for Z
sigma2_Z = 1;  % Variance of base distribution for Z

% Draw Z as lognormal random variable
Z = randn(M,J) * sigma2_Z + mu_Z;

% Set coefficient for pricing equation
gamma_Z = .2;

% Get prices as quality plus price times price coefficient plus disturbance
p = xi + gamma_Z*Z;

% Draw epsilon as Gumbel(0,1) i.i.d. random variables
eps = evrnd(0,1,n,J);

% Set price coefficient for utility function
beta = -.2;

% Construct utility as u_{ij} = beta*p_{ij} + xi_{mj} + eps_{ij}
% The Kronecker product repeats the [1,J] vectors p_j and xi_j exactly n/M
% times for each market, i.e. exactly as many times as there are people in
% the market
u = kron(beta*p+xi,ones(n/M,1)) + eps;

% Get [n,J] indicator matrix of chosen goods, where the [i,J] element is 1
% if individual i chooses good J, and zero otherwise
C = (u == max(u,[],2));

% Get market shares by using accumarray on the choices for each option
S = zeros(M,J);
for i=1:J
    S(:,i) = accumarray(m,C(:,i),[],@mean);
end

eps_hat = zeros(M,J-1);
for j=1:J-1
    [theta_hat,Sigma_hat,eps_hat(:,j)] = ivreg(log(S(:,j))-log(S(:,J)), ...
        [ones(M,1),p(:,j)],[ones(M,1),Z(:,j)]);
    disp([theta_hat, sqrt(diag(Sigma_hat))])
end

%Sigma_hat = eps_hat'*eps_hat;
%L = chol(Sigma_hat/1,'lower');
%Q = chol(Z*((Z'*Z)\Z'),'lower');