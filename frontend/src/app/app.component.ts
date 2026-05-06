import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService, DocumentDetail, DocumentGroup, DocumentListResponse, DocumentSummary, Sentence } from './api.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent implements OnInit {
  clauseTypes: string[] = [];
  documents: DocumentSummary[] = [];
  groups: DocumentGroup[] | null = null;
  selectedDocument: DocumentDetail | null = null;
  search = '';
  clauseFilter = '';
  grouped = false;
  loading = false;
  uploading = false;
  error = '';

  constructor(private readonly api: ApiService) {}

  ngOnInit(): void {
    this.api.getClauseTypes().subscribe((types) => (this.clauseTypes = types));
    this.refreshDocuments();
  }

  refreshDocuments(): void {
    this.loading = true;
    this.error = '';
    this.api.listDocuments(this.search, this.clauseFilter, this.grouped).subscribe({
      next: (response: DocumentListResponse) => {
        this.documents = response.documents;
        this.groups = response.groups;
        this.loading = false;
        if (this.selectedDocument) {
          const stillVisible = this.documents.some((document) => document.id === this.selectedDocument?.id);
          if (!stillVisible) {
            this.selectedDocument = null;
          }
        }
      },
      error: () => {
        this.error = 'Could not load documents.';
        this.loading = false;
      },
    });
  }

  seedExamples(): void {
    this.loading = true;
    this.api.seedExamples().subscribe({
      next: () => this.refreshDocuments(),
      error: () => {
        this.error = 'Could not seed example contracts.';
        this.loading = false;
      },
    });
  }

  selectDocument(document: DocumentSummary): void {
    this.loading = true;
    this.error = '';
    this.api.getDocument(document.id).subscribe({
      next: (detail) => {
        this.selectedDocument = detail;
        this.loading = false;
      },
      error: () => {
        this.error = 'Could not open document.';
        this.loading = false;
      },
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) {
      return;
    }

    this.uploading = true;
    this.error = '';
    this.api.uploadDocument(file).subscribe({
      next: (document) => {
        this.selectedDocument = document;
        this.uploading = false;
        this.refreshDocuments();
        input.value = '';
      },
      error: () => {
        this.error = 'Upload failed. Use a UTF-8 .txt or .md file.';
        this.uploading = false;
        input.value = '';
      },
    });
  }

  updateSentenceLabel(sentence: Sentence, clauseType: string): void {
    const nextLabel = clauseType || null;
    this.api.setLabel(sentence.id, nextLabel).subscribe({
      next: (updated) => {
        sentence.clause_type = updated.clause_type;
        if (this.selectedDocument) {
          this.recalculateSelectedCounts(this.selectedDocument);
        }
        this.refreshDocuments();
      },
      error: () => (this.error = 'Could not update clause label.'),
    });
  }

  documentProgress(document: DocumentSummary): number {
    if (!document.sentence_count) {
      return 0;
    }
    return Math.round((document.labeled_count / document.sentence_count) * 100);
  }

  visibleGroups(): DocumentGroup[] {
    return this.groups ?? [];
  }

  private recalculateSelectedCounts(document: DocumentDetail): void {
    const counts: Record<string, number> = {};
    for (const type of this.clauseTypes) {
      counts[type] = 0;
    }

    let labeled = 0;
    for (const sentence of document.sentences) {
      if (sentence.clause_type) {
        labeled += 1;
        counts[sentence.clause_type] = (counts[sentence.clause_type] ?? 0) + 1;
      }
    }

    document.labeled_count = labeled;
    document.clause_counts = counts;
  }
}
