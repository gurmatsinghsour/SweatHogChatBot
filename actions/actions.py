# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import logging
import random
import requests
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# API Configuration
API_BASE_URL = "http://localhost:8080"
API_PREDICT_ENDPOINT = f"{API_BASE_URL}/predict"
API_REPORT_ENDPOINT = f"{API_BASE_URL}/predict_with_report"
API_DOWNLOAD_ENDPOINT = f"{API_BASE_URL}/download_report"

class ValidateMedicalInfoForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_medical_info_form"

    def validate_age(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate age input and convert to age bracket with conversational feedback."""
        
        # Age bracket mapping dictionary
        age_brackets = {
            (0, 10): "[0-10)",
            (10, 20): "[10-20)", 
            (20, 30): "[20-30)",
            (30, 40): "[30-40)",
            (40, 50): "[40-50)",
            (50, 60): "[50-60)",
            (60, 70): "[60-70)",
            (70, 80): "[70-80)",
            (80, 90): "[80-90)",
            (90, 100): "[90-100)"
        }
        
        # Conversational age responses
        age_responses = {
            (0, 18): ["Great! Youth is on your side for health recovery!", "Young and resilient - that's a positive factor!"],
            (18, 30): ["Perfect! You're in a great age range for health management!", "Your age works in your favor for diabetes management!"],
            (30, 50): ["Excellent! Prime time for taking control of your health!", "This is a perfect age to focus on long-term health strategies!"],
            (50, 70): ["Wise and experienced! Your maturity helps with consistent health management!", "At this stage, your health awareness really pays off!"],
            (70, 100): ["Admirable! Your longevity shows you know how to take care of yourself!", "Age brings wisdom, especially in health management!"]
        }
        
        try:
            # Convert input to integer
            age = int(slot_value)
            
            # Handle invalid ages with humor
            if age < 0:
                funny_responses = [
                    "Time travel isn't covered by our health assessment! Please enter a valid age.",
                    "I appreciate the creativity, but negative ages aren't in my database! What's your real age?",
                    "Unless you're Benjamin Button, I'll need a positive number for your age!"
                ]
                dispatcher.utter_message(text=random.choice(funny_responses))
                return {"age": None}
            elif age > 120:
                superhuman_responses = [
                    "That's quite an age! Please double-check and enter a realistic age.",
                    "If you've really lived that long, I'd love to know your secrets! But for now, please enter a realistic age.",
                    "That would make you superhuman! I need a more typical human age for accurate assessment."
                ]
                dispatcher.utter_message(text=random.choice(superhuman_responses))
                return {"age": None}
            
            # Find the appropriate age bracket and give encouraging feedback
            for (min_age, max_age), bracket in age_brackets.items():
                if min_age <= age < max_age:
                    # Find appropriate encouraging response
                    for (response_min, response_max), responses in age_responses.items():
                        if response_min <= age < response_max:
                            encouragement = random.choice(responses)
                            dispatcher.utter_message(text=f"Perfect! You're {age} years old, which puts you in the {bracket} age bracket. {encouragement}")
                            return {"age": bracket}
                    
                    # Fallback response
                    dispatcher.utter_message(text=f"Perfect! You're in the {bracket} age bracket. Got it!")
                    return {"age": bracket}
            
            # Handle ages 100 and above
            if age >= 100:
                centennial_responses = [
                    f"Wow, {age} years young! You're in the 90+ category. Impressive longevity!",
                    f"Amazing! At {age}, you're a true inspiration! You're in our highest age bracket.",
                    f"Incredible! {age} years of life experience - you're in the 90+ category."
                ]
                dispatcher.utter_message(text=random.choice(centennial_responses))
                return {"age": "[90-100)+"}
            
        except (ValueError, TypeError):
            number_help_responses = [
                "I need a number for your age! Try something like 25, 45, or 67.",
                "Oops! I need your age as a number. For example: 35 or 62.",
                "Let me get a numerical age from you - just type a number like 28 or 54!"
            ]
            dispatcher.utter_message(text=random.choice(number_help_responses))
            return {"age": None}
        
        return {"age": slot_value}
    
    def validate_gender(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate gender input with inclusive and encouraging responses"""
        
        if slot_value:
            gender_lower = slot_value.lower().strip()
            
            # Male variants
            if gender_lower in ['male', 'm', 'man', 'boy', 'guy', 'gentleman']:
                confirmations = [
                    "Got it - Male! Thanks for that info.",
                    "Perfect! Male recorded. Moving forward!",
                    "Excellent! I've noted Male for your demographic info."
                ]
                dispatcher.utter_message(text=random.choice(confirmations))
                return {"gender": "Male"}
            
            # Female variants    
            elif gender_lower in ['female', 'f', 'woman', 'girl', 'lady']:
                confirmations = [
                    "Got it - Female! Thanks for sharing that.",
                    "Perfect! Female recorded. Continuing on!",
                    "Excellent! I've noted Female for your demographic data."
                ]
                dispatcher.utter_message(text=random.choice(confirmations))
                return {"gender": "Female"}
            else:
                help_responses = [
                    "I need either 'Male' or 'Female' for this assessment. Could you clarify?",
                    "Please specify Male or Female for the demographic analysis.",
                    "For this medical assessment, I need Male or Female. Which applies to you?"
                ]
                dispatcher.utter_message(text=random.choice(help_responses))
                return {"gender": None}
        
        return {"gender": None}
    
    def validate_diabetesMed(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate diabetes medication input"""
        
        if slot_value:
            med_lower = slot_value.lower().strip()
            if med_lower in ['yes', 'y', 'true', '1']:
                confirmations = [
                    "Noted - you are taking diabetes medication. That's important for management!",
                    "Great! Diabetes medication usage recorded. Good job staying on top of treatment!",
                    "Perfect! I've noted that you're on diabetes medication. Consistency is key!"
                ]
                dispatcher.utter_message(text=random.choice(confirmations))
                return {"diabetesMed": "Yes"}
            elif med_lower in ['no', 'n', 'false', '0']:
                responses = [
                    "Noted - you are not taking diabetes medication. We'll factor this into the assessment.",
                    "Got it! No diabetes medication currently. This is important information for the analysis.",
                    "Understood - no diabetes medication at this time. Thanks for the clarification!"
                ]
                dispatcher.utter_message(text=random.choice(responses))
                return {"diabetesMed": "No"}
            else:
                help_responses = [
                    "Please answer Yes or No for diabetes medication. Are you currently taking any?",
                    "I need a Yes or No answer about diabetes medication. Currently taking any?",
                    "Simple Yes or No - are you taking diabetes medication right now?"
                ]
                dispatcher.utter_message(text=random.choice(help_responses))
                return {"diabetesMed": None}
        
        return {"diabetesMed": None}

class ActionProcessMedicalData(Action):
    def name(self) -> Text:
        return "action_process_medical_data"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get all the collected medical information
        medical_data = {
            'age': tracker.get_slot('age'),
            'gender': tracker.get_slot('gender'),
            'race': tracker.get_slot('race'),
            'time_in_hospital': tracker.get_slot('time_in_hospital'),
            'admission_type_id': tracker.get_slot('admission_type_id'),
            'discharge_disposition_id': tracker.get_slot('discharge_disposition_id'),
            'admission_source_id': tracker.get_slot('admission_source_id'),
            'num_medications': tracker.get_slot('num_medications'),
            'num_lab_procedures': tracker.get_slot('num_lab_procedures'),
            'num_procedures': tracker.get_slot('num_procedures'),
            'number_diagnoses': tracker.get_slot('number_diagnoses'),
            'number_inpatient': tracker.get_slot('number_inpatient'),
            'number_outpatient': tracker.get_slot('number_outpatient'),
            'number_emergency': tracker.get_slot('number_emergency'),
            'diabetesMed': tracker.get_slot('diabetesMed'),
            'change': tracker.get_slot('change'),
            'A1Cresult': tracker.get_slot('A1Cresult'),
            'max_glu_serum': tracker.get_slot('max_glu_serum'),
            'insulin': tracker.get_slot('insulin'),
            'metformin': tracker.get_slot('metformin')
        }
        
        # Count how many fields are populated
        filled_fields = sum(1 for value in medical_data.values() if value is not None)
        
        completion_messages = [
            f"Excellent! I've collected {filled_fields} pieces of medical information. Now I'm ready to run your diabetes readmission risk analysis!",
            f"Fantastic! Your comprehensive medical profile has {filled_fields} data points. Time for some serious health analytics!",
            f"Perfect! I now have {filled_fields} medical parameters. Let's see what the data reveals about your health!"
        ]
        
        dispatcher.utter_message(text=random.choice(completion_messages))
        
        # Log the collected data for debugging
        logger.info(f"Medical data collected: {filled_fields} fields populated")
        
        return []

class ActionPredictDiabetesReadmission(Action):
    def name(self) -> Text:
        return "action_predict_diabetes_readmission"

    def _prepare_api_payload(self, medical_data: Dict[Text, Any]) -> Dict[Text, Any]:
        """Prepare the payload for the API request"""
        
        # Convert slot values to API-expected format
        def safe_float_convert(value, default=0):
            try:
                return float(value) if value is not None else default
            except (ValueError, TypeError):
                return default
        
        def safe_int_convert(value, default=1):
            try:
                return int(value) if value is not None else default
            except (ValueError, TypeError):
                return default
        
        # Map admission types
        admission_type_map = {
            "Emergency": 1,
            "Urgent": 2, 
            "Elective": 3
        }
        
        # Map discharge dispositions
        discharge_map = {
            "Home": 1,
            "Skilled Nursing Facility": 2,
            "Rehabilitation": 3,
            "Long-term Care": 4,
            "Home Health Care": 5
        }
        
        # Map admission sources
        admission_source_map = {
            "Emergency Room": 1,
            "Physician Referral": 2,
            "Clinic Referral": 3,
            "Transfer from Hospital": 4
        }
        
        payload = {
            "age": medical_data.get("age", "[30-40)"),
            "gender": medical_data.get("gender", "Female"),
            "time_in_hospital": safe_float_convert(medical_data.get("time_in_hospital"), 3),
            "admission_type": admission_type_map.get(medical_data.get("admission_type_id"), 1),
            "discharge_disposition": discharge_map.get(medical_data.get("discharge_disposition_id"), 1),
            "admission_source": admission_source_map.get(medical_data.get("admission_source_id"), 1),
            "num_medications": safe_float_convert(medical_data.get("num_medications"), 5),
            "num_lab_procedures": safe_float_convert(medical_data.get("num_lab_procedures"), 10),
            "num_procedures": safe_float_convert(medical_data.get("num_procedures"), 1),
            "number_diagnoses": safe_float_convert(medical_data.get("number_diagnoses"), 2),
            "number_inpatient": safe_float_convert(medical_data.get("number_inpatient"), 0),
            "number_outpatient": safe_float_convert(medical_data.get("number_outpatient"), 1),
            "number_emergency": safe_float_convert(medical_data.get("number_emergency"), 0),
            "diabetesMed": medical_data.get("diabetesMed", "No"),
            "change": medical_data.get("change", "No"),
            "A1Cresult": medical_data.get("A1Cresult", "None"),
            "max_glu_serum": medical_data.get("max_glu_serum", "None"),
            "insulin": medical_data.get("insulin", "No"),
            "metformin": medical_data.get("metformin", "No"),
            "diagnosis_1": "250.00"  # Default diabetes diagnosis code
        }
        
        return payload

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get all medical data from slots
        medical_data = {
            "age": tracker.get_slot("age"),
            "gender": tracker.get_slot("gender"),
            "race": tracker.get_slot("race"),
            "time_in_hospital": tracker.get_slot("time_in_hospital"),
            "admission_type_id": tracker.get_slot("admission_type_id"),
            "discharge_disposition_id": tracker.get_slot("discharge_disposition_id"),
            "admission_source_id": tracker.get_slot("admission_source_id"),
            "num_medications": tracker.get_slot("num_medications"),
            "num_lab_procedures": tracker.get_slot("num_lab_procedures"),
            "num_procedures": tracker.get_slot("num_procedures"),
            "number_diagnoses": tracker.get_slot("number_diagnoses"),
            "number_inpatient": tracker.get_slot("number_inpatient"),
            "number_outpatient": tracker.get_slot("number_outpatient"),
            "number_emergency": tracker.get_slot("number_emergency"),
            "diabetesMed": tracker.get_slot("diabetesMed"),
            "change": tracker.get_slot("change"),
            "A1Cresult": tracker.get_slot("A1Cresult"),
            "max_glu_serum": tracker.get_slot("max_glu_serum"),
            "insulin": tracker.get_slot("insulin"),
            "metformin": tracker.get_slot("metformin")
        }
        
        analysis_intros = [
            "🤖 Connecting to our advanced AI prediction engine... This is exciting!",
            "🔬 Sending your data to our sophisticated machine learning model...",
            "📊 Processing your medical data through our intelligent risk assessment API..."
        ]
        dispatcher.utter_message(text=random.choice(analysis_intros))
        
        try:
            # Prepare API payload
            api_payload = self._prepare_api_payload(medical_data)
            
            logger.info(f"Sending prediction request to API: {API_PREDICT_ENDPOINT}")
            logger.info(f"Payload: {json.dumps(api_payload, indent=2)}")
            
            # Make API request for prediction
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                API_PREDICT_ENDPOINT,
                json=api_payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                api_result = response.json()
                
                # Extract AI insights from API response
                confidence_score = api_result.get("confidence_score", 0.5)
                ai_remedy = api_result.get("remedy", "No specific insights available")
                status = api_result.get("status", "unknown")
                
                # Convert confidence to risk level
                if confidence_score < 0.3:
                    risk_level = "LOW"
                    risk_color = "🟢"
                elif confidence_score < 0.7:
                    risk_level = "MODERATE" 
                    risk_color = "🟡"
                else:
                    risk_level = "HIGH"
                    risk_color = "🟠"
                
                risk_percentage = round(confidence_score * 100, 1)
                
                # Create comprehensive AI-powered assessment
                assessment_message = f"""
AI-POWERED DIABETES READMISSION RISK ASSESSMENT

{risk_color} **RISK LEVEL: {risk_level}
AI Confidence Score: {confidence_score:.3f}
Estimated Risk Probability: {risk_percentage}%

**AI-GENERATED MEDICAL INSIGHTS:
{ai_remedy}

**PERSONALIZED RECOMMENDATIONS:
Based on the AI analysis, here are key recommendations:
• Follow up with your healthcare team regularly
• Monitor your blood glucose levels consistently
• Maintain medication adherence as prescribed
• Consider lifestyle modifications for optimal health
• Stay proactive about your diabetes management

**MEDICAL DISCLAIMER:**
This AI-powered assessment uses advanced machine learning algorithms and is for informational purposes only. Please discuss these results with your healthcare provider for personalized medical guidance.

**Technical Details:**
- Prediction generated using state-of-the-art ML models
- Analysis based on {len([k for k, v in medical_data.items() if v is not None])} medical parameters
- Real-time processing via secure API endpoint
                """
                
                dispatcher.utter_message(text=assessment_message)
                
                # Ask if user wants a detailed PDF report
                report_offer_messages = [
                    "�📄 Would you like me to generate a comprehensive PDF report of your assessment? Just say 'yes' and I'll create a detailed medical report for you!",
                    "📋 I can create a professional PDF report with all your assessment details. Would you like me to generate that for you?",
                    "🎯 Want a detailed PDF report for your records? I can generate a comprehensive medical assessment document!"
                ]
                dispatcher.utter_message(text=random.choice(report_offer_messages))
                
                logger.info(f"AI Prediction completed successfully: {risk_level} risk, confidence: {confidence_score}")
                
            else:
                # Fallback to local analysis if API fails
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                dispatcher.utter_message(text="🔄 Our AI service is temporarily busy, but I'll provide you with a comprehensive local analysis...")
                
                # Use fallback local analysis
                self._provide_fallback_analysis(dispatcher, medical_data)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API connection error: {str(e)}")
            dispatcher.utter_message(text="🔄 I'm having trouble connecting to our AI service, but don't worry - I'll analyze your data locally...")
            
            # Use fallback local analysis
            self._provide_fallback_analysis(dispatcher, medical_data)
        
        except Exception as e:
            logger.error(f"Unexpected error in prediction: {str(e)}")
            dispatcher.utter_message(text="⚠️ Something unexpected happened, but I'll still provide you with a basic assessment...")
            
            # Use fallback local analysis
            self._provide_fallback_analysis(dispatcher, medical_data)
        
        return []
    
    def _provide_fallback_analysis(self, dispatcher: CollectingDispatcher, medical_data: Dict[Text, Any]):
        """Provide local analysis when API is unavailable"""
        
        # Simple local risk assessment
        risk_factors = 0
        
        try:
            time_in_hospital = float(medical_data.get("time_in_hospital", 0))
            if time_in_hospital > 7:
                risk_factors += 1
        except:
            pass
        
        try:
            inpatient_visits = float(medical_data.get("number_inpatient", 0))
            if inpatient_visits > 2:
                risk_factors += 1
        except:
            pass
        
        if medical_data.get("diabetesMed") == "No":
            risk_factors += 1
        
        if medical_data.get("A1Cresult") in [">7", ">8"]:
            risk_factors += 1
        
        # Determine risk level
        if risk_factors <= 1:
            risk_level = "LOW"
            risk_color = "🟢"
        elif risk_factors <= 2:
            risk_level = "MODERATE"
            risk_color = "🟡"
        else:
            risk_level = "HIGH"
            risk_color = "🟠"
        
        fallback_message = f"""
🏥 **LOCAL DIABETES READMISSION RISK ASSESSMENT**

{risk_color} **RISK LEVEL: {risk_level}**
📊 **Risk Factors Identified: {risk_factors}**

💡 **GENERAL RECOMMENDATIONS:**
• Continue regular medical follow-ups
• Maintain consistent medication schedule
• Monitor blood glucose regularly
• Focus on healthy lifestyle choices

⚕️ **NOTE:** This is a basic assessment. For detailed AI insights, please try again later when our advanced service is available.
        """
        
        dispatcher.utter_message(text=fallback_message)

class ActionGeneratePDFReport(Action):
    def name(self) -> Text:
        return "action_generate_pdf_report"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get all medical data from slots
        medical_data = {
            "age": tracker.get_slot("age"),
            "gender": tracker.get_slot("gender"),
            "race": tracker.get_slot("race"),
            "time_in_hospital": tracker.get_slot("time_in_hospital"),
            "admission_type_id": tracker.get_slot("admission_type_id"),
            "discharge_disposition_id": tracker.get_slot("discharge_disposition_id"),
            "admission_source_id": tracker.get_slot("admission_source_id"),
            "num_medications": tracker.get_slot("num_medications"),
            "num_lab_procedures": tracker.get_slot("num_lab_procedures"),
            "num_procedures": tracker.get_slot("num_procedures"),
            "number_diagnoses": tracker.get_slot("number_diagnoses"),
            "number_inpatient": tracker.get_slot("number_inpatient"),
            "number_outpatient": tracker.get_slot("number_outpatient"),
            "number_emergency": tracker.get_slot("number_emergency"),
            "diabetesMed": tracker.get_slot("diabetesMed"),
            "change": tracker.get_slot("change"),
            "A1Cresult": tracker.get_slot("A1Cresult"),
            "max_glu_serum": tracker.get_slot("max_glu_serum"),
            "insulin": tracker.get_slot("insulin"),
            "metformin": tracker.get_slot("metformin")
        }
        
        dispatcher.utter_message(text="📄 Generating your comprehensive PDF medical report... This may take a moment!")
        
        try:
            # Prepare API payload (reuse the method from prediction action)
            prediction_action = ActionPredictDiabetesReadmission()
            api_payload = prediction_action._prepare_api_payload(medical_data)
            
            logger.info(f"Sending report generation request to API: {API_REPORT_ENDPOINT}")
            
            # Make API request for PDF report generation
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                API_REPORT_ENDPOINT,
                json=api_payload,
                headers=headers,
                timeout=60  # Longer timeout for report generation
            )
            
            if response.status_code == 200:
                # Extract the report filename from response
                report_data = response.json()
                report_filename = report_data.get("report_filename")
                
                if report_filename:
                    download_url = f"{API_DOWNLOAD_ENDPOINT}/{report_filename}"
                    
                    success_messages = [
                        f"🎉 Your PDF report has been generated successfully!",
                        f"📋 Excellent! Your comprehensive medical report is ready!",
                        f"✅ Perfect! Your detailed assessment report has been created!"
                    ]
                    
                    dispatcher.utter_message(text=random.choice(success_messages))
                    
                    dispatcher.utter_message(
                        text=f"""
📄 **YOUR MEDICAL REPORT IS READY!**

🔗 **Download Link:** {download_url}

📊 **Report Contains:**
• Complete risk assessment analysis
• AI-generated medical insights
• Personalized recommendations
• Detailed data summary
• Professional medical formatting

💡 **To download your report:**
You can access your report using the link above, or save it using:
`curl -o medical_report.pdf {download_url}`

⏰ **Report Availability:** Your report will be available for download for the next 24 hours.

🔒 **Privacy Note:** Your report is securely generated and contains your personalized health assessment.
                        """
                    )
                    
                    logger.info(f"PDF report generated successfully: {report_filename}")
                else:
                    dispatcher.utter_message(text="⚠️ Report was generated but download link is not available. Please try again.")
                    
            else:
                logger.error(f"Report generation API failed with status {response.status_code}: {response.text}")
                dispatcher.utter_message(text="❌ I'm having trouble generating your PDF report right now. Please try again in a few moments.")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Report generation API connection error: {str(e)}")
            dispatcher.utter_message(text="🔄 I'm unable to connect to the report generation service at the moment. Please try again later.")
            
        except Exception as e:
            logger.error(f"Unexpected error in report generation: {str(e)}")
            dispatcher.utter_message(text="⚠️ Something went wrong while generating your report. Please try again.")
        
        return []
