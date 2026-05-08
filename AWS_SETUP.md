# AWS Account Setup Guide

This guide walks you through creating an AWS account, setting up an IAM user with admin privileges, and generating the access keys needed to run this workshop.

---

## Step 1 — Create an AWS Account

1. Go to **https://aws.amazon.com** and click **Create an AWS Account**
2. Enter your email address and choose an account name
3. Set a strong root password and click **Continue**
4. Choose **Personal** or **Business** account type and fill in your details
5. Enter your credit/debit card details — AWS needs this for identity verification. You won't be charged unless you exceed the free tier limits
6. Complete phone verification — AWS will call or text you with a code
7. Choose the **Basic (Free)** support plan
8. Click **Complete sign up**

You'll receive a confirmation email. It may take a few minutes for your account to be activated.

> **Important:** Once your account is active, avoid using the root account for day-to-day work. The next step creates a safer IAM user for that purpose.

---

## Step 2 — Create an IAM User with Admin Privileges

**What is an IAM User?**
IAM (Identity and Access Management) is AWS's system for controlling who can access what in your account. An IAM user is a separate identity within your AWS account with its own credentials and permissions — think of it as a named employee badge rather than the master key to the building.

### Why not just use the root account?

The root account has unrestricted access to everything in your AWS account including billing. If those credentials are ever compromised, an attacker has full control. IAM users let you apply the principle of least privilege — grant only what's needed.

### Create the IAM user

1. Sign in to the [AWS Console](https://console.aws.amazon.com) with your root account
2. Search for **IAM** in the top search bar and open it
3. In the left sidebar, click **Users** → **Create user**
4. Enter a username (e.g., `workshop-admin`) and click **Next**
5. On the **Set permissions** page, select **Attach policies directly**
6. Search for and select **AdministratorAccess**

   > This grants full access to all AWS services — appropriate for a workshop environment. In production, you'd scope this down to only the services your application needs.

7. Click **Next** → review the details → click **Create user**

---

## Step 3 — Create an Access Key and Secret Access Key

**Why do you need these?**
When you run code locally (like the notebooks in this workshop), your machine needs a way to prove to AWS that it's allowed to make API calls. Access keys are the credentials that make this possible — they're the equivalent of a username and password for programmatic access. Without them, calls to Bedrock, AgentCore, and other AWS services will fail with authentication errors.

> **Keep these secret.** Anyone with your access key and secret can make AWS API calls on your behalf and potentially incur charges. Never commit them to Git or share them publicly.

### Generate the keys

1. In the IAM console, click on the user you just created (`workshop-admin`)
2. Go to the **Security credentials** tab
3. Scroll down to **Access keys** and click **Create access key**
4. Select **Command Line Interface (CLI)** as the use case
5. Check the confirmation checkbox and click **Next**
6. Optionally add a description tag (e.g., `workshop-local-dev`)
7. Click **Create access key**
8. **Copy both values immediately** — the Secret Access Key is only shown once

   | Key | Example format |
   |---|---|
   | Access Key ID | `*********************` |
   | Secret Access Key | ``*********************`` |

9. Click **Done**

---

## Step 4 — Configure Your Local Machine

Now tell the AWS CLI and SDKs (boto3, Strands) about your credentials.

### Option A — AWS CLI (recommended)

```bash
aws configure
```

You'll be prompted for:

```
AWS Access Key ID:     `*********************`
AWS Secret Access Key: `*********************`
Default region name:   us-east-1
Default output format: json
```

This saves your credentials to `~/.aws/credentials` and region to `~/.aws/config`.

### Option B — Environment variables

Useful if you're switching between multiple accounts or working in CI/CD:

```bash
export AWS_ACCESS_KEY_ID="`*********************`"
export AWS_SECRET_ACCESS_KEY="`*********************`"
export AWS_DEFAULT_REGION="us-east-1"
```

### Verify it works

```bash
aws sts get-caller-identity
```

Expected output:

```json
{
    "UserId": "AIDAIOSFODNN7EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/workshop-admin"
}
```

If you see this, your credentials are working correctly. Head back to the workshop and run `00_setup.ipynb`.

---

## Security Tips

- **Never hardcode credentials** in your notebooks or Python files — always use environment variables or `~/.aws/credentials`
- **Rotate your keys** periodically — in the IAM console under Security credentials → Actions → Rotate
- **Delete keys you no longer need** — each IAM user can have at most 2 active access keys
- **Enable MFA** on your root account — go to IAM → Security recommendations → Add MFA
- When you're done with the workshop, consider **deactivating the access key** in the IAM console to prevent accidental usage
