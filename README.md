# secrets-broker

Human-in-the-loop secret approval broker. Ephemeral form pages on Netlify, Netlify Identity for auth, Python serverless functions for logic.

## Overview

A lightweight broker that intercepts secret requests and routes them through a human approval step before delivering the value to the requester.

## Architecture

Netlify hosts ephemeral approval form pages backed by Python serverless functions; Netlify Identity handles authentication for approvers.

## Setup

Deploy to Netlify, configure environment variables, and install the client library in the requesting service.

## Usage

The client library sends a request; the broker notifies the approver with a one-time form URL; the approver submits the secret; the client receives it.
