export interface MedicalData {
  age?: string;
  gender?: string;
  race?: string;
  time_in_hospital?: string;
  admission_type_id?: string;
  discharge_disposition_id?: string;
  admission_source_id?: string;
  num_medications?: string;
  num_lab_procedures?: string;
  num_procedures?: string;
  number_diagnoses?: string;
  number_inpatient?: string;
  number_outpatient?: string;
  number_emergency?: string;
  diabetesMed?: string;
  change?: string;
  A1Cresult?: string;
  max_glu_serum?: string;
  insulin?: string;
  metformin?: string;
  [key: string]: string | undefined;
}

export interface PredictionResult {
  risk_level: 'LOW' | 'MODERATE' | 'HIGH';
  confidence_score: number;
  recommendations: string[];
  status: string;
}
