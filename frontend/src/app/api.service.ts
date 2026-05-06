import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

export interface Sentence {
  id: number;
  position: number;
  text: string;
  clause_type: string | null;
}

export interface DocumentSummary {
  id: number;
  filename: string;
  title: string;
  created_at: string;
  updated_at: string;
  sentence_count: number;
  labeled_count: number;
  clause_counts: Record<string, number>;
}

export interface DocumentDetail extends DocumentSummary {
  sentences: Sentence[];
}

export interface DocumentGroup {
  group: string;
  documents: DocumentSummary[];
}

export interface DocumentListResponse {
  documents: DocumentSummary[];
  groups: DocumentGroup[] | null;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly baseUrl = environment.apiUrl;

  constructor(private readonly http: HttpClient) {}

  getClauseTypes(): Observable<string[]> {
    return this.http.get<string[]>(`${this.baseUrl}/clause-types`);
  }

  listDocuments(search: string, clauseType: string, grouped: boolean): Observable<DocumentListResponse> {
    let params = new HttpParams();
    if (search.trim()) {
      params = params.set('search', search.trim());
    }
    if (clauseType) {
      params = params.set('clause_type', clauseType);
    }
    if (grouped) {
      params = params.set('group_by', 'clause_type');
    }
    return this.http.get<DocumentListResponse>(`${this.baseUrl}/documents`, { params });
  }

  getDocument(id: number): Observable<DocumentDetail> {
    return this.http.get<DocumentDetail>(`${this.baseUrl}/documents/${id}`);
  }

  uploadDocument(file: File): Observable<DocumentDetail> {
    const form = new FormData();
    form.append('file', file);
    return this.http.post<DocumentDetail>(`${this.baseUrl}/documents`, form);
  }

  setLabel(sentenceId: number, clauseType: string | null): Observable<Sentence> {
    return this.http.patch<Sentence>(`${this.baseUrl}/sentences/${sentenceId}/label`, {
      clause_type: clauseType,
    });
  }

  seedExamples(): Observable<DocumentDetail[]> {
    return this.http.post<DocumentDetail[]>(`${this.baseUrl}/dev/seed`, {});
  }
}
