import { bootstrapApplication } from '@angular/platform-browser';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter, Routes } from '@angular/router';
import { AppComponent } from './app/app.component';
import { DashboardComponent } from './app/dashboard.component';
import { DocumentLabelComponent } from './app/document-label.component';

const routes: Routes = [
  { path: 'dashboard', component: DashboardComponent },
  { path: 'document/:id/label', component: DocumentLabelComponent },
  { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
  { path: '**', redirectTo: 'dashboard' },
];

bootstrapApplication(AppComponent, {
  providers: [provideHttpClient(), provideRouter(routes)],
}).catch((error) => console.error(error));
