# Resume-Boost AI

A full-stack, serverless web application that helps job seekers intelligently tailor their resumes for specific job applications using Generative AI.

## Contributors

This project was developed collaboratively during the [AWS Lambda Hackathon, July 2025].

- [@sainiteshb](https://github.com/sainiteshb) – Full-stack Development, Project Initiation  
- [@AkshithaK7](https://github.com/AkshithaK7) – Backend Logic, Resume Analysis, AI Integration

## Features

- **Achievement Miner**: Transforms passive job responsibilities into powerful, quantified achievements
- **Culture & Values Alignment**: Analyzes company values and suggests edits to resonate with company culture
- **Experience Bridging**: Helps career-changers reframe past experience using target industry terminology
- **Fully Responsive UI**: Modern React interface that works seamlessly on desktop and mobile
- **Serverless & Scalable**: Built on AWS serverless technology for cost-effectiveness and automatic scaling

## Architecture

The application uses a decoupled frontend and backend architecture:

- **Frontend**: React.js SPA with custom CSS for styling
- **Backend**: AWS serverless architecture with:
  - Amazon S3 for file storage
  - AWS Lambda for compute
  - Amazon Bedrock for AI analysis
  - Amazon DynamoDB for data persistence
  - Amazon API Gateway for HTTP endpoints

## Project Structure

```
resume-boost-ai/
├── template.yaml                 # AWS SAM infrastructure template
├── backend/
│   ├── resume-analysis-service/  # Main AI processing Lambda
│   └── get-results-service/      # API results handler Lambda
├── src/                          # React frontend
│   ├── App.jsx                   # Main application component
│   ├── index.css                 # Custom CSS styles
│   └── main.jsx                  # React entry point
├── package.json                  # Frontend dependencies
├── deploy.sh                     # Backend deployment script
└── README.md                     # This file
```

## Quick Start

### Frontend Development (Demo Mode)

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

3. **Test the application**:
   - Open http://localhost:5173 in your browser
   - Upload any PDF file and paste any job description
   - Click "Boost My Resume" to see demo results
   - The app will show sample AI-generated suggestions after 3 seconds

### Backend Deployment

1. **Prerequisites**:
   - AWS CLI configured with appropriate permissions
   - AWS SAM CLI installed
   - Docker (for Lambda builds)

2. **Deploy using the script**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Manual deployment**:
   ```bash
   sam build --use-container
   sam deploy --guided
   ```

### Configuration

After deployment, update the `API_GATEWAY_URL` in `src/App.jsx` with your actual API Gateway endpoint URL and uncomment the real backend interaction code.

## Demo Mode

The application currently runs in demo mode, which means:
- Frontend is fully functional
- UI shows sample AI-generated results
- No backend deployment required for testing
- Real AI analysis requires backend deployment

To enable real AI analysis:
1. Deploy the backend using the instructions above
2. Update the API Gateway URL in `src/App.jsx`
3. Uncomment the real backend interaction code

## AWS Services Used

- **Amazon S3**: Secure file storage for uploaded resumes
- **AWS Lambda**: Serverless compute for processing and API handling
- **Amazon Bedrock**: AI model service for resume analysis
- **Amazon DynamoDB**: NoSQL database for job status and results
- **Amazon API Gateway**: HTTP API for frontend communication
- **AWS IAM**: Security and permissions management

## Data Flow

1. User uploads resume PDF and job description via React frontend
2. File is uploaded to S3 bucket
3. S3 event triggers resume-analysis Lambda function
4. Lambda extracts text from PDF and sends to Amazon Bedrock
5. AI analysis results are stored in DynamoDB
6. Frontend polls API Gateway endpoint for results
7. Results are displayed to user with actionable suggestions

## Key Features Implementation

### Achievement Mining
- Analyzes resume bullet points for passive language
- Suggests action verbs and quantifiable metrics
- Aligns suggestions with job requirements

### Culture Alignment
- Extracts company values from job descriptions
- Identifies cultural keywords and priorities
- Suggests resume edits that echo company culture

## Deployment

### Frontend Deployment
1. Build the React app: `npm run build`
2. Upload `dist/` contents to S3 bucket configured for static website hosting
3. Configure CloudFront for CDN (optional)

### Backend Deployment
1. Ensure AWS credentials are configured
2. Run `./deploy.sh` or `sam deploy --guided` for first deployment
3. Follow prompts to configure stack parameters
4. Note the API Gateway URL for frontend configuration

## Security Considerations

- All Lambda functions use least-privilege IAM roles
- S3 bucket has appropriate CORS configuration
- API Gateway includes CORS headers for frontend access
- DynamoDB uses on-demand billing for cost optimization

## Monitoring and Logging

- CloudWatch Logs for Lambda function monitoring
- DynamoDB metrics for database performance
- S3 access logs for file upload tracking
- API Gateway metrics for endpoint usage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the AWS CloudWatch logs for backend errors
2. Verify API Gateway endpoint configuration
3. Ensure all AWS services are properly configured
4. Check browser console for frontend errors

## Future Enhancements

- Real-time progress updates
- Multiple resume format support
- Advanced ATS optimization
- Integration with job boards
- Resume template generation
- Cover letter optimization
