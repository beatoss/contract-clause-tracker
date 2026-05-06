import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiService, DocumentGroup, DocumentListResponse, DocumentSummary } from './api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
})
export class DashboardComponent implements OnInit {
  clauseTypes: string[] = [];
  documents: DocumentSummary[] = [];
  groups: DocumentGroup[] | null = null;
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

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) {
      return;
    }

    this.uploading = true;
    this.error = '';
    this.api.uploadDocument(file).subscribe({
      next: () => {
        this.uploading = false;
        input.value = '';
        this.refreshDocuments();
      },
      error: () => {
        this.error = 'Upload failed. Use a UTF-8 .txt or .md file.';
        this.uploading = false;
        input.value = '';
      },
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

  trackDocument(_: number, document: DocumentSummary): number {
    return document.id;
  }
}
