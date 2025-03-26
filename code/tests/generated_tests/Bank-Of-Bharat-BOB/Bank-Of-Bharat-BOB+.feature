Feature: Account Management

  Scenario: Create a new bank account
    Given a valid user request with unique email and phone number
    When the "/finance/v1/bank/v4/bharat/create-account" endpoint is called with a POST request
    Then a 201 status code should be returned
    And a UserResponse object containing the newly created account details should be returned

  Scenario: Update existing bank account details
    Given an existing bank account
    And a valid AccountUpdatingDetailsRequest
    When the "/finance/v1/bank/v4/bharat/update-account-details" endpoint is called with a PUT request
    Then a 201 status code should be returned
    And an AccountUpdateDetailsResponse object with updated details should be returned

  Scenario: Delete a bank account
    Given an existing bank account
    And the correct password
    When the "/finance/v1/bank/v4/bharat/delete-account" endpoint is called with a DELETE request and AccountDeleteAccountDetailsRequest
    Then a 202 status code should be returned
    And an AccountDeletedSuccessResponse should be returned

  Scenario: Retrieve bank account details
    Given an existing bank account
    And the correct account number, IFSC code, and password
    When the "/finance/v1/bank/v4/bharat/get-account-details/{accountNumber}/{IFSCCode}/{password}" endpoint is called with a GET request
    Then a 202 status code should be returned
    And an AccountDetailsResponse object containing the account details should be returned

  Scenario: Unsuccessful Account Retrieval - Incorrect Password
    Given an existing bank account
    And an incorrect password
    When the "/finance/v1/bank/v4/bharat/get-account-details/{accountNumber}/{IFSCCode}/{password}" endpoint is called with a GET request
    Then a non-202 status code should be returned


Feature: Account Transactions

  Scenario: Perform a balance enquiry
    Given an existing bank account
    And the correct password
    When the "/finance/v1/bank/v4/bharat/balance-enquiry" endpoint is called with a GET request and BalanceEnquireyRequest
    Then a 202 status code should be returned
    And a BalanceEnquiryResponse object containing the account balance should be returned

  Scenario: Credit money to an account
    Given an existing bank account
    And a valid CreditCredential
    When the "/finance/v1/bank/v4/bharat/credit-money" endpoint is called with a GET request
    Then a 202 status code should be returned
    And a CreditResponse object should be returned

  Scenario: Debit money from an account - Sufficient Funds
    Given an existing bank account with sufficient balance
    And a valid DebitCredential
    When the "/finance/v1/bank/v4/bharat/debit-money" endpoint is called with a GET request
    Then a 202 status code should be returned
    And a DebitedResponse object should be returned

  Scenario: Debit money from an account - Insufficient Funds
    Given an existing bank account with insufficient balance
    And a valid DebitCredential
    When the "/finance/v1/bank/v4/bharat/debit-money" endpoint is called with a GET request
    Then a non-202 status code should be returned
    And an error message indicating insufficient funds should be returned

  Scenario: Transfer money between accounts
    Given two existing bank accounts with sufficient balance in the sender account
    And a valid TransferMoneyRequest
    When the "/transfer/v1/banking/v6/process" endpoint is called with a POST request
    Then a 202 status code should be returned
    And a TransferMoneyResponse object should be returned

  Scenario: Initiate UPI payment from bank account
    Given an existing bank account and a valid UPI ID with sufficient balance
    And a valid AddMoneyFromAccountToUPIRequest
    When the "/finance/v1/bank/v4/bharat/pay-money-from-upi" endpoint is called with a POST request
    Then a 202 status code should be returned
    And an AddMoneyFromAccountToUPIResponse object should be returned

  Scenario: Add money to UPI from bank account
    Given an existing bank account and a valid UPI ID
    And a valid AddMoneyToUPIFromAccountRequest
    When the "/finance/v1/bank/v4/bharat/add-money-to-upi-from-bank" endpoint is called with a POST request
    Then a 202 status code should be returned
    And an AddMoneyToUPIFromAccountResponse object should be returned

  Scenario: Manually update account balance
    Given an existing bank account
    And a valid UpdateAmountManually request
    When the "/finance/v1/bank/v4/bharat/update/money" endpoint is called with a PUT request
    Then a 202 status code should be returned
    And an UpdateAmountResponse object should be returned

Feature: NetBanking and UPI Management

  Scenario: Create a NetBanking ID
    Given an existing bank account
    And a valid NetBankingRequest
    When the "/finance/v1/banking/net-bankingId-create" endpoint is called with a POST request
    Then a 202 status code should be returned
    And a NetBankingResponse object should be returned

  Scenario: Retrieve NetBanking details
    Given an existing bank account
    And a valid GetNetBankingRequest
    When the "/finance/v1/banking/get-internetBanking-details" endpoint is called with a GET request
    Then a 202 status code should be returned
    And a NetBankingResponse object should be returned

  Scenario: Retrieve transaction history
    Given an existing bank account
    When the "/transaction/v1/fetch/transaction-enquiry/{accountNumber}" endpoint is called with a GET request
    Then a 202 status code should be returned
    And a List<TransactionResponse> object should be returned

  Scenario: Create a UPI ID
    Given an existing bank account and NetBanking ID
    And a valid UPIRequest
    When the "/finance/upi/v1/upi-create" endpoint is called with a POST request
    Then a 202 status code should be returned
    And a UPIResponse object should be returned

  Scenario: Retrieve UPI details
    Given an existing bank account with a UPI ID
    And a valid GetUPIRequest
    When the "/finance/upi/v1/get-upi-details" endpoint is called with a GET request
    Then a 202 status code should be returned
    And a UPIResponse object should be returned